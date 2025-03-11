document.addEventListener('DOMContentLoaded', function() {
  const showModalButtons = document.querySelectorAll('.showModalBtn');
  const modal = document.getElementById('dynamicModal');
  const modalLabel = document.getElementById('dynamicModalLabel');
  const modalFormContent = document.getElementById('modal-form-content');
  const closeModalButton = document.querySelector('.modal .close');

  showModalButtons.forEach(button => {
      button.addEventListener('click', function() {
          if (modal.style.display === 'block') {
              // If the modal is already displayed, hide it
              modal.style.display = 'none';
          } else {
              const modalTitle = this.getAttribute('data-modal-title');
              const url = this.getAttribute('data-url');

              // Set the modal title
              modalLabel.innerText = modalTitle;

              // Fetch the form from the server
              fetch(url)
                  .then(response => response.text())
                  .then(html => {
                      // Insert the form into the modal body
                      modalFormContent.innerHTML = html;
                      
                      // Show the modal
                      modal.style.display = 'block';
                  });
          }
      });
  });

  closeModalButton.addEventListener('click', function() {
      modal.style.display = 'none';
  });

  // Close the modal when clicking outside of the modal content
  window.addEventListener('click', function(event) {
      if (event.target == modal) {
          modal.style.display = 'none';
      }
  });
});