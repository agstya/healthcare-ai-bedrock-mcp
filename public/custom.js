// Update the title to be more catchy and professional
document.title = "AI Healthcare Assistant - Revolutionizing Patient Care";

// Create a banner element
const banner = document.createElement("div");
banner.style.backgroundColor = "#2c3e50"; // Dark color for the banner
banner.style.color = "aquamarine"; // Update text color to aquamarine
banner.style.padding = "15px";
banner.style.textAlign = "center";
banner.style.fontSize = "20px";
banner.style.fontWeight = "bold";
banner.textContent = "Empowering Healthcare with AI Solutions";

// Append the banner to the body
document.body.prepend(banner);

// Add an AI healthcare-related image below the banner
const image = document.createElement("img");
image.src = "./public/image.png"; // Adjusted path to ensure the logo renders correctly
image.alt = "AI Healthcare Logo";
image.style.display = "block";
image.style.margin = "20px auto";
image.style.width = "150px"; // Adjust the size as needed

// Append the image below the banner
banner.insertAdjacentElement("afterend", image);

// Add a custom description below the image
const description = document.createElement("p");
description.textContent = "This tool integrates MCP with MIMIC-IV data to assist healthcare professionals and patients (care providers and receivers) by answering healthcare-related questions.";
description.style.textAlign = "center";
description.style.margin = "20px auto";
description.style.fontSize = "16px";
description.style.color = "lightblue"; // Update text color to light blue

// Append the description below the image
image.insertAdjacentElement("afterend", description);