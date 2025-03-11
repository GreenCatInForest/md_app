let loginButton = document.querySelector("#loginButton");
let hamburgerMenuBtn = document.querySelector(".hamburger-menu-btn");
let hamburgerMenuItems = document.querySelector(".hamburger-menu");

let darkModeBtnToggle = document.querySelector("#dark-mode-btn-toggle");
let body = document.body;
// let darkModeAllElementsToggle = document.querySelectorAll(".mode");

let baseNavbarLinks = document.querySelectorAll(".base-navbar-link");
let baseNavbar = document.querySelector("#base-navbar");




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


// Hamburger menu toggle event

document.addEventListener('DOMContentLoaded', () => {
  

  const handleHamburgerMenuBtn = (event) => {
      event.preventDefault();
      console.log("Hamburger menu button clicked");

      hamburgerMenuBtn.classList.toggle('active');


      baseNavbarLinks.forEach(link => {
          link.classList.toggle('hidden');
      });
  };

  // Add click event listener to the hamburger button
  hamburgerMenuBtn.addEventListener('click', handleHamburgerMenuBtn);
});

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
  let isDarkMode = body.classList.toggle("dark");
  const allElements = body.getElementsByTagName("*");
  for (let i = 0; i < allElements.length; i++) {
    allElements[i].classList.toggle("dark");
  }
  localStorage.setItem("isDarkMode", isDarkMode);
};


const handleDarkModeInLs = (event) => {
  event.preventDefault();
  let isDarkMode=localStorage.getItem("isDarkMode");
  if (isDarkMode === "true") {
    body.classList.add("dark");
    const allElements = body.getElementsByTagName("*");
    for (let i = 0; i < allElements.length; i++) {
      allElements[i].classList.toggle("dark");
    }
  }
  else {
    console.log("--dark mode is off--");
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





