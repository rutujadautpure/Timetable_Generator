document.addEventListener('DOMContentLoaded', function() {
    const classesLink = document.getElementById('add-classroom-link');
    const popupContainer = document.getElementById('popup-container');
    const closePopupButton = document.getElementById('close-popup');

    classesLink.addEventListener('click', function(event) {
        event.preventDefault();
        popupContainer.style.display = 'block';
    });

    closePopupButton.addEventListener('click', function() {
        popupContainer.style.display = 'none';
    });
});