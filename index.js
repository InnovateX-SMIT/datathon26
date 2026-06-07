document.addEventListener('DOMContentLoaded', () => {
  // Sidebar Tab Switching Interaction
  const sidebarItems = document.querySelectorAll('.sidebar ul li');
  sidebarItems.forEach(item => {
    item.addEventListener('click', () => {
      sidebarItems.forEach(li => li.classList.remove('active'));
      item.classList.add('active');
    });
  });
});