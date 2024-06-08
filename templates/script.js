document.getElementById('loginForm').addEventListener('submit', function(event) {
    let username = document.getElementById('username').value;
    let regno = document.getElementById('regno').value;
    let email = document.getElementById('email').value;

    if (!username || !regno || !email) {
        alert('All fields are required.');
        event.preventDefault();
    }

    if (!/^\d{12}$/.test(regno)) {
        alert('Register number must be a 6 digit number.');
        event.preventDefault();
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
        alert('Email format is invalid.');
        event.preventDefault();
    }
});
