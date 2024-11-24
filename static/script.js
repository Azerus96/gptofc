document.getElementById("start").addEventListener("click", async () => {
    const response = await fetch("/start", { method: "POST" });
    const data = await response.json();
    renderHand(data.hand);
});

document.getElementById("next").addEventListener("click", async () => {
    const response = await fetch("/next", { method: "POST" });
    const data = await response.json();
    renderHand(data.hand);
});

function renderHand(hand) {
    const handDiv = document.getElementById("hand");
    handDiv.innerHTML = "";
    hand.forEach(card => {
        const cardDiv = document.createElement("div");
        cardDiv.className = "card";
        cardDiv.innerText = card;
        handDiv.appendChild(cardDiv);
    });
}
