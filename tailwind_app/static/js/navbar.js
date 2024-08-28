let loginButton = document.querySelector("#loginButton");
// let hamburgerBtnToggle = document.querySelector("#hamburger-btn-toggle");
// let hamburgerItem = document.querySelectorAll(".hamburger-item");
let darkModeBtnToggle = document.querySelector("#dark-mode-btn-toggle");
let body = document.body;
// let darkModeAllElementsToggle = document.querySelectorAll(".mode");
let helpSupportMenuBtn = document.querySelector("#help-support-menu-btn");
let baseNavbarLinks = document.querySelectorAll(".base-navbar-link");
let baseNavbar = document.querySelector("#base-navbar");


console.log(baseNavbarLinks);

document.addEventListener('DOMContentLoaded', function() {

  const currentPage = window.location.pathname;
  console.log(currentPage);

  baseNavbarLinks.forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
    else {
      link.classList.remove('active');
    }
  });
});






console.log(loginButton);
console.log(darkModeBtnToggle);

// Login button click event

const handleLogin = (event) => {
  event.preventDefault();
  console.log("Login button clicked");
  location.href = event.target.getAttribute("data-url");
};

// Dark mode toggle event

const handleDarkModeBtnToggle = (event) => {
  event.preventDefault();
  console.log("Dark mode button clicked");
  let isLightMode = body.classList.toggle("light");
  const allElements = body.getElementsByTagName("*");
  for (let i = 0; i < allElements.length; i++) {
    allElements[i].classList.toggle("light");
  }
  localStorage.setItem("isLightMode", isLightMode);
};


const handleDarkModeInLs = (event) => {
  event.preventDefault();
  let isLightMode=localStorage.getItem("isLightMode");
  if (isLightMode === "true") {
    body.classList.add("light");
    const allElements = body.getElementsByTagName("*");
    for (let i = 0; i < allElements.length; i++) {
      allElements[i].classList.toggle("light");
    }
  }
  else {
    console.log("--dark mode is on");
  }
}


// Event listeners
window.addEventListener("load", handleDarkModeInLs);

loginButton
?loginButton.addEventListener("click", handleLogin)
:null;

darkModeBtnToggle.addEventListener("click", handleDarkModeBtnToggle);


let hiddenMenuPropertiesBtn = document.querySelector("#hidden-menu-properties");
let hiddenMenuPropertiesItems = document.querySelector(".hidden-menu-item");
console.log(hiddenMenuPropertiesBtn);
console.log(hiddenMenuPropertiesItems);

const toggleHiddenMenu = (event) => {
  event.preventDefault();
  console.log("Hidden menu properties button clicked");
  hiddenMenuPropertiesItems.classList.toggle("hidden");
}

// hiddenMenuPropertiesBtn.addEventListener("click", toggleHiddenMenu);





