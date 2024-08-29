document.addEventListener('DOMContentLoaded', function () {
const btnLoginForm = document.querySelector('#btn-login-form-toggle');
const btnRegisterForm = document.querySelector('#btn-register-form-toggle');
const loginForm = document.querySelector('.login-form');
const registerForm = document.querySelector('.register-form');


btnLoginForm.addEventListener('click', () => {
    btnLoginForm.style.backgroundColor = '#21264D';
    btnRegisterForm.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';

    loginForm.style.left = '50%';
    registerForm.style.left = '-50%';
});

btnRegisterForm.addEventListener('click', () => {
    btnLoginForm.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
    btnRegisterForm.style.backgroundColor = '#21264D';

    loginForm.style.left = '-50%';
    registerForm.style.left = '50%';
})});
