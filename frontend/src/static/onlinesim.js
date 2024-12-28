document.addEventListener('DOMContentLoaded', async () => {
    const countriesDropdown = document.getElementById('countries');
    const numbersDropdown = document.getElementById('numbers');
    const resultsContainer = document.getElementById('results-container');
	const updateCacheButton = document.getElementById('update-cache');

    // Fetch and populate countries
	async function fetchCountries() {
		try {
			const response = await fetch('/api/numbers/countries');
			const data = await response.json();

			console.log('Full API Response:', data); // Debug log

			// Check if 'countries' exists and is an object
			if (data && typeof data.countries === 'object') {
				const countryKeys = Object.keys(data.countries);
				console.log('Extracted Country Keys:', countryKeys); // Debug log

				// Populate the dropdown
				countriesDropdown.innerHTML = countryKeys.map(
					country => `<option value="${country}">${country.charAt(0).toUpperCase() + country.slice(1)}</option>`
				).join('');

				// Automatically fetch numbers for the first country
				if (countryKeys.length > 0) {
					fetchNumbers(countryKeys[0], data.countries[countryKeys[0]]);
				}
			} else {
				console.warn('No valid countries found in response');
				countriesDropdown.innerHTML = '<option value="">No countries available</option>';
			}
		} catch (error) {
			console.error('Error fetching countries:', error);
			resultsContainer.innerHTML = '<div class="error">Failed to load countries.</div>';
		}
	}

    // Function to trigger cache update
	async function updateCache() {
		console.log('Cache update button clicked');
		try {
			// Changed the method to use GET
			const response = await fetch('/api/update', {
				method: 'GET', // Specify GET request
				headers: {
					'Content-Type': 'application/json',
				},
			});
			const data = await response.json();
			console.log('Cache update response:', data);
			if (data.status === 'success') {
				alert('Cache updated successfully.');
			} else {
				alert('Failed to update cache.');
			}
		} catch (error) {
			console.error('Error updating cache:', error);
			alert('Error updating cache.');
		}
	}

    // Populate numbers for a specific country
	async function fetchNumbers(country, numbers) {
		try {
			if (!numbers) {
				const response = await fetch(`/api/numbers/${country}`);
				numbers = await response.json();
			}
			console.log(`Numbers for ${country}:`, numbers); // Debug log
			if (Array.isArray(numbers)) {
				numbersDropdown.innerHTML = numbers.map(
					number => `
					<option value="${number.full_number}">
						${number.full_number} (${number.age})
					</option>`
				).join('');

				// Add copy buttons for each number
				resultsContainer.innerHTML = numbers.map(
					number => `
					<div class="result">
						<span>${number.full_number} (${number.age})</span>
						<button class="copy-number" data-number="${number.full_number}">Copy Number</button>
					</div>`
				).join('');

				// Attach event listeners to copy buttons
				document.querySelectorAll('.copy-number').forEach(button => {
					button.addEventListener('click', () => {
						const numberToCopy = button.getAttribute('data-number');
						copyToClipboard(numberToCopy);
					});
				});
			} else {
				numbersDropdown.innerHTML = '<option value="">No numbers available</option>';
				resultsContainer.innerHTML = '<div class="error">No numbers found.</div>';
			}
		} catch (error) {
			console.error(`Error fetching numbers for country ${country}:`, error);
			resultsContainer.innerHTML = '<div class="error">Failed to load numbers.</div>';
		}
	}

    // Fetch and display SMS messages for the selected number
	async function fetchSMS() {
		const country = countriesDropdown.value;
		const number = numbersDropdown.value;

		if (!country || !number) {
			resultsContainer.innerHTML = '<div class="error">Please select a country and a number.</div>';
			return;
		}

		try {
			const response = await fetch(`/api/sms/${country}/${number}`);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data = await response.json();
			console.log(`SMS for ${number} in ${country}:`, data); // Debug log
			if (data.sms && Array.isArray(data.sms)) {
				// Extract codes and render with copy buttons
				resultsContainer.innerHTML = data.sms.map(sms => {
					const codeMatch = sms.text.match(/\b\d{4,6}\b/); // Match 4-6 digit code
					if (codeMatch) {
						const code = codeMatch[0];
						return `
							<div class="result">
								<span class="sms-text">${sms.text}</span>
								<button class="copy-button" data-code="${code}">Copy Code</button>
							</div>`;
					}
					return `<div class="result"><span class="sms-text">${sms.text}</span></div>`;
				}).join('');

				// Add event listeners for copy buttons
				document.querySelectorAll('.copy-button').forEach(button => {
					button.addEventListener('click', () => {
						const code = button.getAttribute('data-code');
						copyToClipboard(code);
					});
				});
			} else {
				resultsContainer.innerHTML = '<div class="result">No SMS found.</div>';
			}
		} catch (error) {
			console.error(`Error fetching SMS for number ${number}:`, error);
			resultsContainer.innerHTML = '<div class="error">Failed to fetch SMS</div>';
		}
	}

// Copy to clipboard function with fallback
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
            .then(() => alert(`Copied code: ${text}`))
            .catch(err => console.error('Error copying text: ', err));
    } else {
        // Fallback: Use a temporary input element
        const tempInput = document.createElement('input');
        tempInput.value = text;
        document.body.appendChild(tempInput);
        tempInput.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Fallback: Unable to copy', err);
        }
        document.body.removeChild(tempInput);
    }
}

    if (updateCacheButton) {
        updateCacheButton.addEventListener('click', updateCache);
        console.log('Update cache button is ready.');
    } else {
        console.error('Update cache button not found in DOM');
    }

    // Event listeners
    countriesDropdown.addEventListener('change', () => {
        const selectedCountry = countriesDropdown.value;
        fetchNumbers(selectedCountry);
    });

    document.getElementById('fetch-sms').addEventListener('click', fetchSMS);

    // Initialize page with countries
    await fetchCountries();
});
