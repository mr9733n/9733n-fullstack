    // Copy element
    function copyText(element) {
        const textToCopy = element.getAttribute('data-result');
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
    // "Copy" events handler
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            copyText(button.previousElementSibling); 
            button.classList.remove('initial');
            button.classList.add('copied'); 
        });
    });