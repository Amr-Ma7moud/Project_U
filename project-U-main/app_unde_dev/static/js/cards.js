 // Function to handle card expansion
 function toggleCard(button) {
    const clickedCard = button.closest('.card');
    const isExpanded = clickedCard.classList.contains('expanded');
    
    // Remove expanded class from all cards
    document.querySelectorAll('.card').forEach(card => {
        card.classList.remove('expanded');
    });
    
    // Toggle the clicked card
    if (!isExpanded) {
        clickedCard.classList.add('expanded');
    }
}

// Drag to scroll functionality
// const slider = document.querySelector('.cards-container');
// let isDown = false;
// let startX;
// let scrollLeft;

// slider.addEventListener('mousedown', (e) => {
//     isDown = true;
//     slider.style.cursor = 'grabbing';
//     startX = e.pageX - slider.offsetLeft;
//     scrollLeft = slider.scrollLeft;
// });

// slider.addEventListener('mouseleave', () => {
//     isDown = false;
//     slider.style.cursor = 'grab';
// });

// slider.addEventListener('mouseup', () => {
//     isDown = false;
//     slider.style.cursor = 'grab';
// });

// slider.addEventListener('mousemove', (e) => {
//     if (!isDown) return;
//     e.preventDefault();
//     const x = e.pageX - slider.offsetLeft;
//     const walk = (x - startX) * 2;
//     slider.scrollLeft = scrollLeft - walk;
// });

// Auto scroll when mouse is near the edges
// let scrollInterval;
// slider.addEventListener('mousemove', (e) => {
//     const container = slider.getBoundingClientRect();
//     const mouseX = e.clientX - container.left;
    
//     clearInterval(scrollInterval);
    
//     if (mouseX > container.width - 50) {
//         scrollInterval = setInterval(() => {
//             slider.scrollLeft += 5;
//         }, 16);
//     } else if (mouseX < 50) {
//         scrollInterval = setInterval(() => {
//             slider.scrollLeft -= 5;
//         }, 16);
//     }
// });

// slider.addEventListener('mouseleave', () => {
//     clearInterval(scrollInterval);
// });