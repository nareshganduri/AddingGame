async function loadRanks() {
    let game_mode = document.getElementById('gameModeSelect').value;

    let response = await fetch(`/ranks/${game_mode}`, {
        method:'POST'
    });
    let results = await response.json();

    let ranksTable = document.getElementById('resultsTable');
    ranksTable.innerHTML = '';
    for (let i = 0; i < results.length; i++) {
        let result = results[i];
        let username = result.username;
        let final_score = result.final_score;
        let total_time = result.total_time;

        ranksTable.innerHTML += `<tr>
            <th scope="row">${i + 1}</th>
            <td>${username}</td>
            <td>${total_time}</td>
            <td>${final_score}%</td>
        </tr>`;
    }
}