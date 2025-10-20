const token = localStorage.getItem('jwt');
if (!token) {
  window.location.href = "/";
}
