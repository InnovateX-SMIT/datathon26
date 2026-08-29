import re
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter
from datetime import datetime

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.logging import logger
from backend.core.dataset_resolver import DatasetResolver
from backend.schemas.modus_operandi import (
    MOAttributes,
    MOProfileResponse,
    SimilarCaseMatch,
    AssociatedSuspect,
    OffenderBehavioralProfileResponse,
    OffenderCaseSummary,
    CrossJurisdictionLink,
    CrossJurisdictionSummary
)

class ModusOperandiService:
    """
    Modus Operandi (MO) & Behavioral Intelligence Service.
    Extracts structured behavioral profiles from case narratives, computes
    reproducible TF-IDF cosine similarity, discovers cross-jurisdiction patterns,
    and builds repeat-offender behavioral profiles.
    """

    # Controlled rule-based vocabularies for genuine behavioral extraction
    ENTRY_RULES = [
        (r"\b(rear\s+window|broken\s+window|window\s+entry|window\s+shattered)\b", "Rear Window / Window Breach"),
        (r"\b(forced\s+entry|door\s+broken|lock\s+broken|lock\s+picked|padlock\s+cut|door\s+breach)\b", "Forced Door / Lock Breach"),
        (r"\b(roof\s+entry|drilling\s+wall|wall\s+cut|tunneling)\b", "Structural Penetration (Roof/Wall)"),
        (r"\b(phishing|malicious\s+link|fake\s+email|credential\s+harvesting|fake\s+domain)\b", "Phishing / Credential Infiltration"),
        (r"\b(dark\s+web|tor\s+network|onion\s+routing|hidden\s+service)\b", "Dark Web Infiltration / Hidden Network"),
        (r"\b(unauthorized\s+access|server\s+breach|sql\s+injection|system\s+intrusion|hacked)\b", "System Intrusion / Unauthorized Access"),
        (r"\b(impersonat(ion|ing)|disguise|fake\s+official|false\s+identity|identity\s+theft)\b", "Impersonation / Pretext Entry"),
        (r"\b(snatch(ing|ed)|intercept(ed|ion)|waylaid|ambush)\b", "Physical Interception / Ambush")
    ]

    WEAPON_TOOL_RULES = [
        (r"\b(knife|blade|dagger|machete|chopper|sword)\b", "Sharp Weapon / Blade"),
        (r"\b(iron\s+rod|crowbar|cutter|drill|hammer|wrench|blunt\s+weapon)\b", "Mechanical Breaching Tool / Rod"),
        (r"\b(firearm|gun|pistol|revolver|country\s+made\s+pistol|bullets)\b", "Firearm / Pistol"),
        (r"\b(crypto\s+mixer|tumbler|mixer\s+service|monero|smart\s+contract)\b", "Crypto Tumbler / Mixer Utility"),
        (r"\b(botnet|malware|trojan|keylogger|ransomware|script)\b", "Malware / Exploit Payload"),
        (r"\b(fake\s+sim|cloned\s+sim|spoofed\s+caller\s+id|burner\s+phone)\b", "Spoofed Telecom / Burner SIM"),
        (r"\b(forged\s+document|counterfeit|fake\s+stamp|fake\s+certificate)\b", "Forged Documents / Fake Instruments")
    ]

    TARGET_RULES = [
        (r"\b(residential|apartment|independent\s+house|villa|flat|home)\b", "Residential Premise"),
        (r"\b(shop|store|showroom|mall|commercial\s+complex|retail)\b", "Commercial / Retail Establishment"),
        (r"\b(bank|atm|cash\s+counter|financial\s+institution|nbfc)\b", "Financial / ATM Infrastructure"),
        (r"\b(crypto\s+exchange|digital\s+wallet|crypto\s+account|decentralized\s+wallet)\b", "Digital Asset / Crypto Wallet"),
        (r"\b(computer\s+resource|server|database|data\s+center|cloud\s+account)\b", "IT / Server Infrastructure"),
        (r"\b(pedestrian|commuter|elderly|woman|minor|student|victim)\b", "Individual / Vulnerable Citizen"),
        (r"\b(vehicle|car|two\s*wheeler|motorcycle|truck|cargo)\b", "Vehicle / Transit Asset"),
        (r"\b(warehouse|factory|godown|industrial\s+unit)\b", "Industrial / Storage Facility")
    ]

    APPROACH_RULES = [
        (r"\b(dark\s+web\s+crime|tor\s+market|darknet\s+trade)\b", "Darknet Transaction & Anonymized Channel"),
        (r"\b(cheating\s+by\s+personation|identity\s+theft|otp\s+fraud|sim\s+swap)\b", "Social Engineering & Digital Deception"),
        (r"\b(money\s+laundering|shell\s+companies|hawala|smurfing)\b", "Financial Layering & Obfuscation"),
        (r"\b(night\s+time|stealth|under\s+cover\s+of\s+darkness)\b", "Covert Night Operation"),
        (r"\b(gang|syndicate|group\s+of\s+accused|joint\s+operation|multiple\s+persons)\b", "Coordinated Group Operation"),
        (r"\b(extortion|ransom|blackmail|intimidation|threat)\b", "Intimidation & Extortionate Demand"),
        (r"\b(drug\s+peddling|narcotics\s+supply|contraband\s+smuggling)\b", "Illicit Substance Distribution")
    ]

    ESCAPE_RULES = [
        (r"\b(motorcycle|two\s*wheeler|bike\s+getaway)\b", "Motorcycle Quick Getaway"),
        (r"\b(car|four\s*wheeler|van|suv|stolen\s+vehicle)\b", "Motor Vehicle Transit Escape"),
        (r"\b(on\s+foot|fled\s+scene|ran\s+away)\b", "Foot Evacuation"),
        (r"\b(cross\s*border\s+crypto|tumbler\s+transfer|multi\s*hop\s+wallet)\b", "Layered Crypto Hopping"),
        (r"\b(proxy\s+chain|vpn\s+routing|ip\s+spoofing)\b", "Virtual IP / Proxy Evasion"),
        (r"\b(hawala|cash\s+courier|mule\s+account)\b", "Mule Account / Layered Hawala")
    ]

    LOCATION_RULES = [
        (r"\b(cyber\s+space|electronic\s+realm|internet|online|virtual)\b", "Digital / Virtual Domain"),
        (r"\b(isolated\s+area|highway|outer\s+ring\s+road|unlit\s+stretch)\b", "Isolated Highway / Peripheral Sector"),
        (r"\b(market|bazaar|crowded\s+place|bus\s+stand|railway\s+station)\b", "High-Density Transit / Market Zone"),
        (r"\b(gated\s+society|layout|residential\s+colony)\b", "Suburban Residential Colony"),
        (r"\b(industrial\s+area|tech\s+park|commercial\s+hub)\b", "Commercial / Industrial District")
    ]

    def __init__(self, db: Session):
        self.db = db

    def _get_active_id(self) -> Optional[int]:
        return DatasetResolver(self.db).get_active_dataset_id_optional()

    def _get_schema_type(self) -> str:
        return DatasetResolver(self.db).get_active_dataset_schema_type()

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        # Remove timestamps, standard police case headers, boilerplate phrases
        cleaned = text.strip()
        cleaned = re.sub(r"On\s+\d{2}-\d{2}-\d{4},?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Investigation taken up under\s+.*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Incident occurred near coordinates\s+[\d\.\,\s\-]+within the jurisdiction of\s+[^.]*\.?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def extract_mo(
        self,
        raw_text: Optional[str],
        occurrence_text: Optional[str] = None,
        section_descs: Optional[List[str]] = None,
        crime_head: Optional[str] = None,
        crime_group: Optional[str] = None,
        incident_time: Optional[datetime] = None
    ) -> Tuple[MOAttributes, List[str], str, bool]:
        """
        Extracts structured behavioral attributes and tags from narrative and statutory text.
        Returns: (attributes_model, behavioral_tags, mo_summary, is_sufficient)
        """
        combined_text = " ".join(filter(None, [
            raw_text or "",
            occurrence_text or "",
            " ".join(section_descs or []),
            crime_head or "",
            crime_group or ""
        ])).strip()

        if not combined_text or len(combined_text) < 5:
            return (
                MOAttributes(),
                [],
                "MO unavailable / insufficient text",
                False
            )

        text_lower = combined_text.lower()
        extracted_entry = None
        extracted_weapon = None
        extracted_target = None
        extracted_time = None
        extracted_approach = None
        extracted_escape = None
        extracted_location = None
        behavioral_tags: List[str] = []

        # 1. Entry
        for pattern, label in self.ENTRY_RULES:
            if re.search(pattern, text_lower):
                extracted_entry = label
                behavioral_tags.append(label)
                break

        # 2. Weapon / Tool
        for pattern, label in self.WEAPON_TOOL_RULES:
            if re.search(pattern, text_lower):
                extracted_weapon = label
                behavioral_tags.append(label)
                break

        # 3. Target
        for pattern, label in self.TARGET_RULES:
            if re.search(pattern, text_lower):
                extracted_target = label
                behavioral_tags.append(label)
                break

        # 4. Temporal pattern
        if incident_time:
            hour = incident_time.hour
            if 0 <= hour < 5:
                extracted_time = "Late Night / Nocturnal (00:00 - 05:00)"
            elif 5 <= hour < 12:
                extracted_time = "Morning Operation (05:00 - 12:00)"
            elif 12 <= hour < 17:
                extracted_time = "Daytime Operation (12:00 - 17:00)"
            else:
                extracted_time = "Evening / Night Operation (17:00 - 24:00)"
            behavioral_tags.append(extracted_time)
        elif "night" in text_lower or "midnight" in text_lower:
            extracted_time = "Night-time Operation"
            behavioral_tags.append(extracted_time)
        elif "morning" in text_lower:
            extracted_time = "Early Morning Operation"
            behavioral_tags.append(extracted_time)
        elif "daylight" in text_lower or "afternoon" in text_lower:
            extracted_time = "Broad Daylight Operation"
            behavioral_tags.append(extracted_time)

        # 5. Approach
        for pattern, label in self.APPROACH_RULES:
            if re.search(pattern, text_lower):
                extracted_approach = label
                behavioral_tags.append(label)
                break

        # 6. Escape / Laundering
        for pattern, label in self.ESCAPE_RULES:
            if re.search(pattern, text_lower):
                extracted_escape = label
                behavioral_tags.append(label)
                break

        # 7. Location context
        for pattern, label in self.LOCATION_RULES:
            if re.search(pattern, text_lower):
                extracted_location = label
                behavioral_tags.append(label)
                break

        # Additional statutory behavioral tags if head/group present
        if crime_head and crime_head.strip() and crime_head not in behavioral_tags:
            behavioral_tags.append(crime_head.strip())

        # Fallback summary construction
        summary_parts = []
        if extracted_approach:
            summary_parts.append(f"Approach: {extracted_approach}")
        if extracted_entry:
            summary_parts.append(f"Entry: {extracted_entry}")
        if extracted_weapon:
            summary_parts.append(f"Tool/Vector: {extracted_weapon}")
        if extracted_target:
            summary_parts.append(f"Target: {extracted_target}")
        if extracted_time:
            summary_parts.append(f"Timing: {extracted_time}")
        if extracted_escape:
            summary_parts.append(f"Evasion: {extracted_escape}")

        if summary_parts:
            mo_summary = " • ".join(summary_parts)
            is_sufficient = True
        else:
            # Cleaned facts narrative
            cleaned = self._clean_text(raw_text)
            if cleaned and len(cleaned) > 10:
                mo_summary = f"Identified Pattern: {cleaned}"
                is_sufficient = True
            else:
                mo_summary = "MO unavailable / insufficient text"
                is_sufficient = False

        attributes = MOAttributes(
            entry_method=extracted_entry,
            weapon_tool=extracted_weapon,
            target_type=extracted_target,
            time_pattern=extracted_time,
            approach_method=extracted_approach,
            escape_method=extracted_escape,
            location_type=extracted_location
        )

        return (attributes, list(dict.fromkeys(behavioral_tags)), mo_summary, is_sufficient)

    def _build_case_text_corpus(self, cases: List[Any], schema_type: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Builds normalized text document representations for all cases in dataset for TF-IDF vectorization.
        """
        documents = []
        case_metas = []

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_organization import Unit
            from backend.models.fir_geography import District

            for case in cases:
                brief = case.BriefFacts or ""
                occ_brief = case.occurrence_time.BriefFacts if case.occurrence_time else ""
                crime_head = case.crime_minor_head.CrimeHeadName if case.crime_minor_head else ""
                crime_group = case.crime_major_head.CrimeGroupName if case.crime_major_head else ""
                gravity = case.gravity_offence.name if case.gravity_offence else ""
                sec_descs = [
                    assoc.section.SectionDescription for assoc in case.act_sections if assoc.section and assoc.section.SectionDescription
                ]
                inc_time = case.occurrence_time.IncidentFromDate if case.occurrence_time else None

                attrs, tags, summary, suff = self.extract_mo(
                    raw_text=brief,
                    occurrence_text=occ_brief,
                    section_descs=sec_descs,
                    crime_head=crime_head,
                    crime_group=crime_group,
                    incident_time=inc_time
                )

                # Combined feature text
                doc = " ".join(filter(None, [
                    crime_head,
                    crime_group,
                    gravity,
                    " ".join(sec_descs),
                    " ".join(tags),
                    summary if suff else "",
                    self._clean_text(brief),
                    self._clean_text(occ_brief)
                ])).lower()

                station_name = case.police_station.name if case.police_station else "Unknown Station"
                district_name = "Unknown District"
                if case.police_station and case.police_station.DistrictID:
                    dist = self.db.query(District).filter(District.id == case.police_station.DistrictID).first()
                    if dist:
                        district_name = dist.name

                suspects = [
                    AssociatedSuspect(
                        accused_id=acc.id,
                        name=acc.AccusedName,
                        person_id=acc.PersonID,
                        age=acc.AgeYear,
                        gender=acc.gender.name if acc.gender else None
                    )
                    for acc in case.accused
                ]

                documents.append(doc)
                case_metas.append({
                    "case_id": case.id,
                    "crime_no": case.CrimeNo,
                    "case_no": case.CaseNo,
                    "crime_type": crime_head or crime_group or "Unclassified Crime",
                    "district": district_name,
                    "police_station": station_name,
                    "registered_date": str(case.CrimeRegisteredDate) if case.CrimeRegisteredDate else None,
                    "brief_facts": brief,
                    "attributes": attrs,
                    "tags": tags,
                    "summary": summary,
                    "is_sufficient": suff,
                    "suspects": suspects
                })
        else:
            for crime in cases:
                desc = crime.description or ""
                c_type = crime.crime_type or ""
                c_cat = crime.crime_category or ""
                c_sub = crime.crime_subcategory or ""

                attrs, tags, summary, suff = self.extract_mo(
                    raw_text=desc,
                    crime_head=c_sub or c_type,
                    crime_group=c_cat
                )

                doc = " ".join(filter(None, [
                    c_type,
                    c_cat,
                    c_sub,
                    " ".join(tags),
                    summary if suff else "",
                    self._clean_text(desc)
                ])).lower()

                district_name = crime.location.district if crime.location else "Unknown District"
                station_name = crime.police_station.station_name if crime.police_station else "Unknown Station"

                suspects = []
                for p in crime.participations:
                    if p.criminal:
                        suspects.append(AssociatedSuspect(
                            accused_id=p.criminal.id,
                            name=p.criminal.name,
                            person_id=None,
                            age=int(p.criminal.age) if p.criminal.age else None,
                            gender=p.criminal.gender
                        ))

                documents.append(doc)
                case_metas.append({
                    "case_id": crime.id,
                    "crime_no": f"CR-{crime.id}",
                    "case_no": f"CASE-{crime.id}",
                    "crime_type": c_type or c_cat or "Unclassified Crime",
                    "district": district_name,
                    "police_station": station_name,
                    "registered_date": str(crime.crime_date) if crime.crime_date else None,
                    "brief_facts": desc,
                    "attributes": attrs,
                    "tags": tags,
                    "summary": summary,
                    "is_sufficient": suff,
                    "suspects": suspects
                })

        return documents, case_metas

    def get_case_mo_profile(self, case_id: int) -> Optional[MOProfileResponse]:
        """
        Retrieves the structured MO profile, top behaviorally similar cases,
        and associated suspects for a specific case.
        """
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            target_case = self.db.query(CaseMaster).filter(CaseMaster.id == case_id).first()
            if not target_case:
                return None

            all_cases = self.db.query(CaseMaster).filter(
                CaseMaster.dataset_id == active_id if active_id else True
            ).all()
        else:
            from backend.models.crime import CrimeEvent
            target_case = self.db.query(CrimeEvent).filter(CrimeEvent.id == case_id).first()
            if not target_case:
                return None

            all_cases = self.db.query(CrimeEvent).filter(
                CrimeEvent.dataset_id == active_id if active_id else True
            ).all()

        if not all_cases:
            return None

        # Build corpus & metadata
        docs, metas = self._build_case_text_corpus(all_cases, schema_type)

        target_idx = None
        for idx, meta in enumerate(metas):
            if meta["case_id"] == case_id:
                target_idx = idx
                break

        if target_idx is None:
            return None

        target_meta = metas[target_idx]

        # Calculate TF-IDF Cosine Similarities across cases
        similar_cases = []
        if len(docs) > 1 and any(len(d.strip()) > 0 for d in docs):
            try:
                vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")
                tfidf_matrix = vectorizer.fit_transform(docs)
                target_vec = tfidf_matrix[target_idx]
                sim_scores = cosine_similarity(target_vec, tfidf_matrix).flatten()

                target_tags_set = set(target_meta["tags"])

                # Rank by similarity descending
                ranked_indices = np.argsort(sim_scores)[::-1]

                for idx in ranked_indices:
                    if idx == target_idx:
                        continue
                    score = float(sim_scores[idx])
                    if score < 0.10: # Minimum threshold to eliminate complete non-matches
                        continue

                    other_meta = metas[idx]
                    other_tags_set = set(other_meta["tags"])
                    matching_traits = list(target_tags_set.intersection(other_tags_set))

                    is_cross = (other_meta["district"] != target_meta["district"] or other_meta["police_station"] != target_meta["police_station"])

                    similar_cases.append(SimilarCaseMatch(
                        case_id=other_meta["case_id"],
                        crime_no=other_meta["crime_no"],
                        case_no=other_meta["case_no"],
                        crime_type=other_meta["crime_type"],
                        district=other_meta["district"],
                        police_station=other_meta["police_station"],
                        registered_date=other_meta["registered_date"],
                        similarity_score=round(score, 4),
                        similarity_percentage=int(round(score * 100)),
                        is_cross_jurisdiction=is_cross,
                        matching_attributes=matching_traits,
                        associated_suspects=other_meta["suspects"]
                    ))

                    if len(similar_cases) >= 10:
                        break
            except Exception as e:
                logger.error(f"Error computing TF-IDF similarity for case {case_id}: {e}", exc_info=True)

        return MOProfileResponse(
            case_id=target_meta["case_id"],
            crime_no=target_meta["crime_no"],
            case_no=target_meta["case_no"],
            crime_type=target_meta["crime_type"],
            district=target_meta["district"],
            police_station=target_meta["police_station"],
            registered_date=target_meta["registered_date"],
            raw_narrative=target_meta["brief_facts"],
            is_sufficient=target_meta["is_sufficient"],
            mo_summary=target_meta["summary"],
            attributes=target_meta["attributes"],
            behavioral_tags=target_meta["tags"],
            associated_suspects=target_meta["suspects"],
            similar_cases=similar_cases
        )

    def find_similar_cases(
        self,
        case_id: int,
        limit: int = 10,
        min_similarity: float = 0.20
    ) -> List[SimilarCaseMatch]:
        """
        Discovers top behaviorally similar cases for a given case ID.
        """
        profile = self.get_case_mo_profile(case_id)
        if not profile:
            return []
        return [
            c for c in profile.similar_cases
            if c.similarity_score >= min_similarity
        ][:limit]

    def get_offender_behavioral_profile(self, accused_id: int) -> Optional[OffenderBehavioralProfileResponse]:
        """
        Aggregates recurring MO patterns for an offender across all their associated cases.
        """
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_people import Accused
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District

            acc = self.db.query(Accused).filter(Accused.id == accused_id).first()
            if not acc:
                return None

            # Find all cases featuring this accused name
            filters = [
                Accused.AccusedName == acc.AccusedName
            ]
            if active_id:
                filters.append(CaseMaster.dataset_id == active_id)

            cases = self.db.query(CaseMaster).join(Accused).filter(*filters).all()

            if not cases:
                return None

            all_tags: List[str] = []
            crime_types: List[str] = []
            districts: List[str] = []
            case_summaries: List[OffenderCaseSummary] = []

            for c in cases:
                c_type = c.crime_minor_head.CrimeHeadName if c.crime_minor_head else (c.crime_major_head.CrimeGroupName if c.crime_major_head else "Unclassified Crime")
                crime_types.append(c_type)

                station_name = c.police_station.name if c.police_station else "Unknown Station"
                dist_name = "Unknown District"
                if c.police_station and c.police_station.DistrictID:
                    dist = self.db.query(District).filter(District.id == c.police_station.DistrictID).first()
                    if dist:
                        dist_name = dist.name
                districts.append(dist_name)

                sec_descs = [
                    assoc.section.SectionDescription for assoc in c.act_sections if assoc.section and assoc.section.SectionDescription
                ]

                _, tags, summary, _ = self.extract_mo(
                    raw_text=c.BriefFacts,
                    occurrence_text=c.occurrence_time.BriefFacts if c.occurrence_time else None,
                    section_descs=sec_descs,
                    crime_head=c_type
                )
                all_tags.extend(tags)

                case_summaries.append(OffenderCaseSummary(
                    case_id=c.id,
                    crime_no=c.CrimeNo,
                    crime_type=c_type,
                    registered_date=str(c.CrimeRegisteredDate) if c.CrimeRegisteredDate else None,
                    district=dist_name,
                    police_station=station_name,
                    mo_summary=summary,
                    behavioral_tags=tags
                ))

            # Identify recurring signatures (tags occurring in >= 2 cases or most frequent if >= 2 cases)
            tag_counts = Counter(all_tags)
            recurring = [tag for tag, count in tag_counts.items() if count >= 2]
            if not recurring and len(cases) >= 2:
                recurring = [tag for tag, count in tag_counts.most_common(3)]

            has_history = len(cases) >= 2

            return OffenderBehavioralProfileResponse(
                accused_id=acc.id,
                name=acc.AccusedName,
                person_id=acc.PersonID,
                total_associated_cases=len(cases),
                has_sufficient_history=has_history,
                recurring_mo_signatures=recurring if has_history else ["Single documented incident on record"],
                primary_crime_types=list(dict.fromkeys(crime_types)),
                primary_districts=list(dict.fromkeys(districts)),
                associated_cases=case_summaries
            )
        else:
            from backend.models.criminal import Criminal
            criminal = self.db.query(Criminal).filter(Criminal.id == accused_id).first()
            if not criminal:
                return None

            cases = [
                p.crime_event for p in criminal.participations
                if p.crime_event and (active_id is None or p.crime_event.dataset_id == active_id)
            ]

            all_tags = []
            crime_types = []
            districts = []
            case_summaries = []

            for ce in cases:
                c_type = ce.crime_type or ce.crime_category or "Unclassified Crime"
                crime_types.append(c_type)
                dist_name = ce.location.district if ce.location else "Unknown District"
                districts.append(dist_name)
                station_name = ce.police_station.station_name if ce.police_station else "Unknown Station"

                _, tags, summary, _ = self.extract_mo(
                    raw_text=ce.description,
                    crime_head=c_type
                )
                all_tags.extend(tags)

                case_summaries.append(OffenderCaseSummary(
                    case_id=ce.id,
                    crime_no=f"CR-{ce.id}",
                    crime_type=c_type,
                    registered_date=str(ce.crime_date) if ce.crime_date else None,
                    district=dist_name,
                    police_station=station_name,
                    mo_summary=summary,
                    behavioral_tags=tags
                ))

            tag_counts = Counter(all_tags)
            recurring = [tag for tag, count in tag_counts.items() if count >= 2]
            has_history = len(cases) >= 2

            return OffenderBehavioralProfileResponse(
                accused_id=criminal.id,
                name=criminal.name,
                person_id=None,
                total_associated_cases=len(cases),
                has_sufficient_history=has_history,
                recurring_mo_signatures=recurring if has_history else ["Single documented incident on record"],
                primary_crime_types=list(dict.fromkeys(crime_types)),
                primary_districts=list(dict.fromkeys(districts)),
                associated_cases=case_summaries
            )

    def get_cross_jurisdiction_patterns(
        self,
        min_similarity: float = 0.50,
        limit: int = 25
    ) -> CrossJurisdictionSummary:
        """
        Identifies cross-border MO matches where cases in District A share strong
        behavioral similarity with cases in District B.
        """
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            all_cases = self.db.query(CaseMaster).filter(
                CaseMaster.dataset_id == active_id if active_id else True
            ).limit(200).all() # Sample 200 cases for fast, representative cross-district analysis
        else:
            from backend.models.crime import CrimeEvent
            all_cases = self.db.query(CrimeEvent).filter(
                CrimeEvent.dataset_id == active_id if active_id else True
            ).limit(200).all()

        if len(all_cases) < 2:
            return CrossJurisdictionSummary(
                total_cross_jurisdiction_patterns=0,
                jurisdiction_pairs=[],
                sample_links=[]
            )

        docs, metas = self._build_case_text_corpus(all_cases, schema_type)

        cross_links: List[CrossJurisdictionLink] = []
        pair_counts: Dict[Tuple[str, str], List[float]] = {}

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(docs)
            sim_mat = cosine_similarity(tfidf_matrix)

            n = len(metas)
            for i in range(n):
                for j in range(i + 1, n):
                    score = float(sim_mat[i, j])
                    if score < min_similarity:
                        continue

                    m_i = metas[i]
                    m_j = metas[j]

                    d_i = m_i["district"]
                    d_j = m_j["district"]

                    if d_i != d_j and d_i != "Unknown District" and d_j != "Unknown District":
                        # Match found across distinct districts
                        common_tags = list(set(m_i["tags"]).intersection(set(m_j["tags"])))
                        pair_key = tuple(sorted([d_i, d_j]))
                        if pair_key not in pair_counts:
                            pair_counts[pair_key] = []
                        pair_counts[pair_key].append(score)

                        cross_links.append(CrossJurisdictionLink(
                            source_case_id=m_i["case_id"],
                            source_crime_no=m_i["crime_no"],
                            source_district=d_i,
                            target_case_id=m_j["case_id"],
                            target_crime_no=m_j["crime_no"],
                            target_district=d_j,
                            crime_type=m_i["crime_type"],
                            similarity_score=round(score, 4),
                            similarity_percentage=int(round(score * 100)),
                            matching_attributes=common_tags
                        ))
        except Exception as e:
            logger.error(f"Error computing cross jurisdiction MO patterns: {e}", exc_info=True)

        cross_links.sort(key=lambda x: x.similarity_score, reverse=True)

        jurisdiction_pairs = []
        for (d1, d2), scores in sorted(pair_counts.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
            jurisdiction_pairs.append({
                "district_a": d1,
                "district_b": d2,
                "linked_cases_count": len(scores),
                "avg_similarity": round(float(np.mean(scores)), 3),
                "max_similarity": round(float(np.max(scores)), 3)
            })

        return CrossJurisdictionSummary(
            total_cross_jurisdiction_patterns=len(cross_links),
            jurisdiction_pairs=jurisdiction_pairs,
            sample_links=cross_links[:limit]
        )
