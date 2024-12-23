let lastMousePosition = { x: 0, y: 0 };
let lastCatPosition = { x: 0, y: 0 };
let isCursorMoving = false;
let stationaryTimer = null;
let stopMoving = false;

document.addEventListener("mousemove", function (e) {
    const floatingImage = document.querySelector(".cat");
    if (!floatingImage) return;

    const mouseX = e.pageX;
    const mouseY = e.pageY;

    const catRect = floatingImage.getBoundingClientRect();
    const catX = catRect.left + catRect.width / 2;
    const catY = catRect.top + catRect.height / 2;

    const dx = mouseX - catX;
    const dy = mouseY - catY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    isCursorMoving = mouseX !== lastMousePosition.x || mouseY !== lastMousePosition.y;

    if (stopMoving) return; // Stop moving the cat after 5 minutes of inactivity

    if (distance < 50) {
        // Jump away if too close
        const angle = Math.atan2(dy, dx);
        const offsetX = -10 * dx; // Double the distance away
        const offsetY = -10 * dy; // Double the distance away
        floatingImage.style.left = `${catX + offsetX - catRect.width / 2}px`;
        floatingImage.style.top = `${catY + offsetY - catRect.height / 2}px`;
    } else {
        // Gradually move the cat closer to the cursor
        const moveX = catX + dx * 0.05;
        const moveY = catY + dy * 0.05;
        floatingImage.style.left = `${moveX - catRect.width / 2}px`;
        floatingImage.style.top = `${moveY - catRect.height / 2}px`;
    }

    // Reset the stationary timer on mouse move
    clearTimeout(stationaryTimer);
    stationaryTimer = setTimeout(() => {
        if (!isCursorMoving) {
            stopMoving = true; // Stop the cat after 5 minutes
        }
    }, 5 * 60 * 1000); // 5 minutes in milliseconds

    // Update positions
    lastMousePosition = { x: mouseX, y: mouseY };
    lastCatPosition = { x: catX, y: catY };
});

// Reset cat's starting position and logic on load
window.onload = function () {
    const floatingImage = document.querySelector(".cat");
    if (floatingImage) {
        const catRect = floatingImage.getBoundingClientRect();
        lastCatPosition = {
            x: catRect.left + catRect.width / 2,
            y: catRect.top + catRect.height / 2,
        };
    }
};
