let modalDashboard = document.querySelector('#modal-dashboard');
const modalDashboardPlaceHolder = document.querySelector('#modal-dashboard-placeholder');
const modalDashboardContents = document.querySelectorAll('.user-dashboard-article');
const modalDashboardClose = document.querySelector('#modal-dashboard-close');

const modalDashboardTitle = document.querySelector('#modal-dashboard-title');
const modalDashboardContent = document.querySelector('#modal-dashboard-content');
let inner_content = '';
let title = '';
let paragraphs = '';


document.addEventListener('DOMContentLoaded', () => {

modalDashboardContents.forEach((content) => {

    content.addEventListener('click', (event) => {
        event.target.style.color = "purple";
        content.classList.add('border', 'border-gray-300', 'shadow-md');
        modalDashboard.classList.remove('hidden');
        modalDashboardPlaceHolder.classList.remove('hidden');

        let title = content.querySelector('h3').innerHTML;
        let paragraphs = content.querySelectorAll('p');
        let inner_content = '';
        console.log(inner_content);
        console.log(paragraphs);

        paragraphs.forEach((paragraph) => {
            inner_content += paragraph.innerHTML + ' ';
        });

        title ? modalDashboardTitle.innerText = title
        : '';

        inner_content ? modalDashboardContent.innerText = inner_content
        : '';

        
    });
});

modalDashboardClose.addEventListener('click', (event) => {
    event.preventDefault();
    console.log('close');

    modalDashboard.classList.add('hidden');
    modalDashboardPlaceHolder.classList.add('hidden');
    modalDashboardTitle.innerText = '';
    modalDashboardContent.innerText = '';
    title = '';
    inner_content = '';
    paragraphs = '';
});

});