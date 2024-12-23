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

    let moveX, moveY;

    if (distance < 64) {
        // Jump away if too close
        const angle = Math.atan2(dy, dx);
        const offsetX = -50 * dx; // Jump further away
        const offsetY = -50 * dy; // Jump further away
        moveX = catX + offsetX;
        moveY = catY + offsetY;
    } else {
        // Gradually move the cat closer to the cursor
        moveX = catX + dx * 0.02;
        moveY = catY + dy * 0.02;
    }

    // Ensure the cat stays within the browser window
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    const catWidth = catRect.width;
    const catHeight = catRect.height;

    moveX = Math.max(catWidth / 2, Math.min(windowWidth - catWidth / 2, moveX));
    moveY = Math.max(catHeight / 2, Math.min(windowHeight - catHeight / 2, moveY));

    // Position the cat
    floatingImage.style.left = `${moveX - catWidth / 2}px`;
    floatingImage.style.top = `${moveY - catHeight / 2}px`;

    // Apply transformations for flipping or rotating
    if (mouseX < catRect.left) {
        floatingImage.style.transform = "scaleX(-1)"; // Flip horizontally
    } else if (mouseY < catRect.top) {
        floatingImage.style.transform = "scaleY(-1)"; // Flip vertically
    } else {
        floatingImage.style.transform = "scale(1)"; // Reset to normal
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
