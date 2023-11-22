document.getElementById("minutesSlider").addEventListener("input", function() {
    document.getElementById("selectedMinutes").textContent = "Selected minutes: " + this.value;
  });
  
  document.getElementById("forecastButton").addEventListener("click", function() {
    const selectedMinutes = document.getElementById("minutesSlider").value;
    fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"ticker": "MSFT", "n_minutes": selectedMinutes}),
    })
    .then(response => response.json())
    .then(data => {
      const table = document.querySelector("table");
      table.innerHTML = `
        <tr>
          <th>MSFT</th>
          <th>Date</th>
          <th>Time</th>
          <th>Volatility</th>
        </tr>`;
      let rowNumber = 1;
      for (const [timestamp, volatility] of Object.entries(data.forecast)) {
        const [date, time] = timestamp.split("T");
        const className = rowNumber % 2 === 0 ? "even" : "odd";
        table.innerHTML += `
          <tr class="${className}">
            <td>${rowNumber}</td>
            <td>${date}</td>
            <td>${time}</td>
            <td>${volatility}</td>
          </tr>`;
        rowNumber++;
      }
    })
    .catch(error => {
      const table = document.querySelector("table");
      table.innerHTML = `<tr><td colspan="4">Error: ${error.message}</td></tr>`;
    });
  });
  
  document.getElementById("resetButton").addEventListener("click", function() {
    // Clear the table
    const table = document.querySelector("table");
    table.innerHTML = `
      <tr>
        <th>Microsoft Corporation Volatility By Minute</th>
        <th>Date</th>
        <th>Time</th>
        <th>Volatility</th>
      </tr>`;
  });
  
  // Add interactivity to the title with moving colors
  const title = document.getElementById("interactiveTitle");
  setInterval(function() {
    const randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
    title.style.color = randomColor;
  }, 1000); // Change the interval as needed
  