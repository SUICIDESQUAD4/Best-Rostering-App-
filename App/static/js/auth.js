document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const userType = document.querySelector('input[name="userType"]:checked')?.value;

    try {
      const response = await fetch("/api/v1/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        // store the token
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userType", userType);

        // redirect to appropriate dashboard
        if (userType === "admin") {
          window.location.href = "/admin/dashboard";
        } else {
          window.location.href = "/staff/dashboard";
        }
      } else {
        alert(data.message || "Invalid credentials. Please try again.");
      }
    } catch (err) {
      console.error(err);
      alert("Login failed. Check your connection.");
    }
  });
});
