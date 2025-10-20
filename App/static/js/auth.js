document.getElementById("login-btn").addEventListener("click", async () => {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.getElementById("role").value;
  const errorMsg = document.getElementById("error-msg");

  if (!username || !password) {
    errorMsg.textContent = "Username and password required.";
    return;
  }

  const res = await fetch("/api/v1/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok && data.access_token) {
    localStorage.setItem("jwt", data.access_token);
    if (role === "admin") {
      window.location.href = "/admin/dashboard";
    } else {
      window.location.href = "/staff/dashboard";
    }
  } else {
    errorMsg.textContent = data.msg || "Login failed";
  }
});
