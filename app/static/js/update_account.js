function confirmAccountUpdate() {
    /**
     * Confirms if the input of the emails and passwords are the same when signing up an account.
     */
    let email = document.getElementById('emailInput');
    let confirmEmail = document.getElementById('emailConfirmInput');
    let emailMsg = (email.value === confirmEmail.value && confirmEmail.value != "") ? "" : "Email must be matching.";

    let password = document.getElementById('passwordInput');
    let confirmPassword = document.getElementById('passwordConfirmInput');
    let passwordMsg = (password.value === confirmPassword.value && confirmPassword.value != "") ? "" : "Password must be matching."

    confirmEmail.setCustomValidity(emailMsg);
    confirmPassword.setCustomValidity(passwordMsg);
}