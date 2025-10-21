// static/js/protect.js
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem('token');
  const type = localStorage.getItem('userType');

  // No token = send back to login
  if (!token) {
    window.location.href = "/";
    return;
  }

  const path = window.location.pathname;

  // Prevent staff accessing admin pages
  if (path.startsWith("/admin") && type !== "admin") {
    window.location.href = "/";
  }

  // Prevent admin accessing staff pages
  if (path.startsWith("/staff") && type !== "staff") {
    window.location.href = "/";
  }
});
