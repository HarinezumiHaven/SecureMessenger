// check token
document.addEventListener("DOMContentLoaded", function() {
    const token = localStorage.getItem("authToken");

    // switch button display
    if (token) {
        document.getElementById("home-btn").style.display = "block";
        document.getElementById("show-login").style.display = "none";
        document.getElementById("show-register").style.display = "none";
    }
});

// register show
document.getElementById("show-register").addEventListener("click", function() {
    document.getElementById("register-form").style.display = "block";
    document.getElementById("login-form").style.display = "none";
});

// login show
document.getElementById("show-login").addEventListener("click", function() {
    document.getElementById("login-form").style.display = "block";
    document.getElementById("register-form").style.display = "none";
});

// register check
document.getElementById("register").addEventListener("submit", function(event) {
    event.preventDefault();
    let email = document.getElementById("reg-email").value;
    let password = document.getElementById("reg-password").value;

    fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error("Error:", error));
});

// login check
document.getElementById("login").addEventListener("submit", function(event) {
    event.preventDefault();
    let email = document.getElementById("login-email").value;
    let password = document.getElementById("login-password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            alert("Login successful!");
            localStorage.setItem("authToken", data.token);
            document.getElementById("home-btn").style.display = "block";
            document.getElementById("show-login").style.display = "none";
            document.getElementById("show-register").style.display = "none";
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error("Error:", error));
});

// home page
document.getElementById("home-btn").addEventListener("click", function() {
    let token = localStorage.getItem("authToken");
    if (!token) {
        alert("You need to log in first!");
        return;
    }

    fetch("http://127.0.0.1:5000/home", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "http://127.0.0.1:5000/home";
        } else {
            alert("Access denied. Only verified users can access Home.");
        }
    })
    .catch(error => console.error("Error:", error));
});