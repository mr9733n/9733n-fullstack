document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('theme-toggle');
    const disableAnimationsButton = document.getElementById('disable-animations');
    const catElement = document.querySelector('.cat');

    // Locate the pacman.css stylesheet
    const pacmanStylesheet = Array.from(document.styleSheets).find(
        sheet => sheet.href && sheet.href.includes('pacman.css')
    );

    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            const darkModeOn = !getDarkModeState();
            setDarkModeState(darkModeOn);
            updateDarkMode(darkModeOn);
        });
    }

    if (disableAnimationsButton) {
        disableAnimationsButton.addEventListener('click', () => {
            const animationsDisabled = !getAnimationsState();
            setAnimationsState(animationsDisabled);
            updateAnimations(animationsDisabled, catElement, pacmanStylesheet);
            // Reload the page to ensure changes take effect globally
            location.reload();
        });
    }

    // Initialize states
    updateDarkMode(getDarkModeState());
    updateAnimations(getAnimationsState(), catElement, pacmanStylesheet);
});

function setDarkModeState(state) {
    localStorage.setItem('darkMode', state ? 'on' : 'off');
}

function getDarkModeState() {
    return localStorage.getItem('darkMode') === 'on';
}

function setAnimationsState(state) {
    localStorage.setItem('animationsDisabled', state ? 'on' : 'off');
}

function getAnimationsState() {
    return localStorage.getItem('animationsDisabled') === 'on';
}

function updateDarkMode(enabled) {
    if (enabled) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

function updateAnimations(disabled, catElement, pacmanStylesheet) {
    if (disabled) {
        document.body.classList.add('animations-disabled');
        if (catElement) {
            catElement.style.display = 'none';
        }
        if (pacmanStylesheet) {
            pacmanStylesheet.disabled = true;
        }
    } else {
        document.body.classList.remove('animations-disabled');
        if (catElement) {
            catElement.style.display = '';
        }
        if (pacmanStylesheet) {
            pacmanStylesheet.disabled = false;
        }
    }
}
