async function predict() {
    const input = document.getElementById('input').value;
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: input })
    });
    const data = await response.json();
    document.getElementById('output').innerText = `Prediction: ${data.prediction}`;
}