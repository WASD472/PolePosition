const API = "http://localhost:8000";
let driversData = []; 
const SESSION_NAMES = {
  FP1: "Практика 1",
  FP2: "Практика 2",
  FP3: "Практика 3",
  QUALIFYING: "Квалификация",
  SPRINT: "Спринт",
  SPRINT_QUALIFYING: "Спринт-квалификация",
  RACE: "Гонка",
};


function toMsk(date, time) {
    const dt = new Date(`${date}T${time}Z`);
    dt.setHours(dt.getHours() + 3);
    const h = String(dt.getHours()).padStart(2, "0");
    const m = String(dt.getMinutes()).padStart(2, "0");
    return `${h}:${m}`;
}


function loadCircuits() {
  fetch(`${API}/circuits/`)
    .then((response) => response.json())
    .then((data) => {
      const content = document.getElementById("circuits-content");
      content.innerHTML = "";

      data.forEach((c) => {
        content.innerHTML += `
            <div class="card">
                <h3>${c.name}</h3>
                <p>${c.locality}, ${c.country}</p>
            </div>
            `;
      });
    });
}

function loadDrivers() {
  fetch(`${API}/drivers/`)
    .then((response) => response.json())
    .then((data) => {
        driversData = data;
        renderDrivers(driversData)

    });
}


function renderDrivers(data){ //Сортировка
      const content = document.getElementById("drivers-content");
      content.innerHTML = "";

      data.forEach((d) => {
        content.innerHTML += `
            <div class="card">
                <h3>${d.first_name} ${d.last_name} #${d.number}</h3>
                <p>${d.code} · ${d.nationality}</p>
                <span class="wins_podiums">Победы: ${d.wins}</span> · <span class="podiums">Подиумы: ${d.podiums}</span>
            </div>
            `;
      });
}


function loadConstructors() {
  fetch(`${API}/constructors/`)
    .then((response) => response.json())
    .then((data) => {
      const content = document.getElementById("constructors-content");
      content.innerHTML = "";

      data.forEach((c) => {
        content.innerHTML += `
            <div class="card">
                <h3>${c.name}</h3>
                <p>${c.short_name} · ${c.country}</p>
            </div>
            `;
      });
    });
}

function loadGrandprix() {
  fetch(`${API}/grandprix/`)
    .then((response) => response.json())
    .then((data) => {
      const content = document.getElementById("grandprix-content");
      content.innerHTML = "";

      data.forEach((g) => {
        content.innerHTML += `
            <div class="card" data-id="${g.id}">
            <h3>${g.name}</h3>
            <p>Этап ${g.round} · ${g.date}</p>
            <div class="sessions"></div> 
            <div class="session-details"></div>
            </div>
            `;
            //Sessions - список сессий
            //sessions details - что показать при клике на сессию
      });

      const cards = document.querySelectorAll("#grandprix-content .card"); //Анимация карточки - (1)
      cards.forEach((card) => {
        card.addEventListener("click", () => {
          toggleSessions(card);
        });
      });
    });
}


function toggleSessions(card) {
    const sessionsDiv = card.querySelector(".sessions");
    const gpId = card.dataset.id;

    if (sessionsDiv.classList.contains("open")) {
        sessionsDiv.classList.remove("open");
        card.classList.remove("open");
        card.querySelector(".session-details").innerHTML="";
        card.querySelectorAll(".session-item").forEach((s) => s.classList.remove("q-open"));
        return;
    }

    document.querySelectorAll("#grandprix-content .sessions").forEach((s) => {
        s.classList.remove("open");
    });
    document.querySelectorAll("#grandprix-content .card").forEach((c) => {
        c.classList.remove("open");
    });

    fetch(`${API}/racesessions/?grand_prix_id=${gpId}`)
        .then(response => response.json())
        .then(data => {
            data.sort((a, b) => {
                const dateA = new Date(`${a.date}T${a.time}Z`);
                const dateB = new Date(`${b.date}T${b.time}Z`);
                return dateA - dateB;
            });

            sessionsDiv.innerHTML = "";

            data.forEach((s) => {
                const displayName = SESSION_NAMES[s.name] || s.name;
                sessionsDiv.innerHTML += `
                    <p class="session-item" data-session-id="${s.id}" data-session-type="${s.type}">
                        <strong>${displayName}</strong>
                        <span>${s.date} ${toMsk(s.date, s.time)}</span>
                    </p>
                `;
            });

            sessionsDiv.classList.add("open");
            card.classList.add("open");

            // обработчики кликов на сессии ===
            sessionsDiv.querySelectorAll(".session-item").forEach((item) => {
                item.addEventListener("click", (e) => {
                    e.stopPropagation();
                    toggleSessionDetails(item, card);
                });
            });
        });
}

function toggleSessionDetails(sessionItem, card) {
    const detailsDiv = card.querySelector(".session-details");
    const sessionId = sessionItem.dataset.sessionId;
    const sessionType = sessionItem.dataset.sessionType;

    // Если эта сессия уже открыта — закрываем
    if (sessionItem.classList.contains("q-open")) {
        sessionItem.classList.remove("q-open");
        detailsDiv.innerHTML = "";
        return;
    }

    // Снять подсветку со всех сессий
    card.querySelectorAll(".session-item").forEach((s) => {
        s.classList.remove("q-open");
    });

    // Пометить текущую
    sessionItem.classList.add("q-open");

    // Очистить контейнер
    detailsDiv.innerHTML = "";

    // === QUALIFYING ===
    if (sessionType === "qualifying") {
        Promise.all([
            fetch(`${API}/qualifying/?session_id=${sessionId}`).then(r => r.json()),
            fetch(`${API}/drivers/`).then(r => r.json())
        ]).then(([qualifying, drivers]) => {
            const driverMap = {};
            drivers.forEach(d => driverMap[d.id] = `${d.first_name} ${d.last_name}`);

            qualifying.sort((a, b) => parseInt(a.position) - parseInt(b.position));

            let html = `<div class="q-results"><table class="q-table">`;
            html += `<thead><tr><th>Поз</th><th>Пилот</th><th>Q1</th><th>Q2</th><th>Q3</th></tr></thead><tbody>`;

            qualifying.forEach(q => {
                const name = driverMap[q.driver_id] || `ID ${q.driver_id}`;
                html += `<tr>
                    <td>${q.position}</td>
                    <td>${name}</td>
                    <td>${q.q1 || "—"}</td>
                    <td>${q.q2 || "—"}</td>
                    <td>${q.q3 || "—"}</td>
                </tr>`;
            });

            html += `</tbody></table></div>`;
            detailsDiv.innerHTML = html;
        });
    }

    // === RACE ===
    else if (sessionType === "race") {
        Promise.all([
            fetch(`${API}/results/?session_id=${sessionId}`).then(r => r.json()),
            fetch(`${API}/drivers/`).then(r => r.json())
        ]).then(([results, drivers]) => {
            const driverMap = {};
            drivers.forEach(d => driverMap[d.id] = `${d.first_name} ${d.last_name} #${d.number}`);

            results.sort((a, b) => parseInt(a.position) - parseInt(b.position));

            let html = `<div class="race-results">`;
            results.forEach(r => {
                const name = driverMap[r.driver_id] || `ID ${r.driver_id}`;
                html += `<p><strong>${r.position}. ${name}</strong><span>${r.points} очков</span></p>`;
            });
            html += `</div>`;
            detailsDiv.innerHTML = html;
        });
    }

    // === ОСТАЛЬНЫЕ (FP1, FP2, FP3, sprint) ===
    else {
        detailsDiv.innerHTML = `<p class="placeholder">Нет данных</p>`;
    }
}




function updateCountdown(session, countdownDiv) {
    const now = new Date()
    const sessionTime = new Date(`${session.date}T${session.time}Z`);
    const diff = sessionTime - now;

    if (diff <= 0){
        countdownDiv.innerHTML = `<p>Сессия уже началась</p>`;
        return;
    }

    const days = Math.floor(diff / 86_400_000);
    const AfterDays = diff % 86_400_000;
    const hours = Math.floor(AfterDays / 3_600_000);
    const AfterHours = AfterDays % 3_600_000;
    const minutes = Math.floor(AfterHours / 60_000);

    const displayName = SESSION_NAMES[session.name] || session.name;

    countdownDiv.innerHTML=`
    <p>
    До начала <strong>"${displayName}"</strong> - 
    ${days} д. ${hours} ч. ${minutes} мин.
    </p>
    `;
}






function loadNextGp() {
  fetch(`${API}/grandprix/`)
    .then((response) => response.json())
    .then((data) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);


      //Фильтрует будущие гп
      const future = data
        .filter((g) => new Date(g.date) >= today)
        .sort((a, b) => new Date(a.date) - new Date(b.date));

      const container = document.getElementById("next-gp");

      if (future.length === 0) {
        container.innerHTML = "<p class='placeholder'>Сезон завершен</p>";
        return;
      }

      const gp = future[0];
      container.innerHTML=`
            <div class= "next-gp-card">
            <h2>${gp.name}</h2>
            <p class="next-gp-info">Этап ${gp.round} - ${gp.date}</p>
            <div class="next-gp-sessions" id="next-gp-sessions"></div>
            <div class="next-gp-countdown" id="next-gp-countdown"></div>
            </div>
        `;

        //Загружаем сессии
        fetch(`${API}/racesessions/?grand_prix_id=${gp.id}`)
            .then(response => response.json())
            .then(sessions => {
                sessions.sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`));
                const sessionsDiv = document.getElementById("next-gp-sessions");
                sessions.forEach(s => {
                    const displayName = SESSION_NAMES[s.name] || s.name;
                    sessionsDiv.innerHTML += `
                    <p>
                    <strong>${displayName}</strong>
                    <span>${s.date} ${toMsk(s.date, s.time)}</span>
                    </p>
                    `;
                });

                const nextSession = sessions //После рендера сессий нашли ближайшую будущую
                .filter(s => new Date(`${s.date}T${s.time}Z`) > new Date())//Отфильтровал будущие
                .sort((a, b) => new Date(`${a.date}T${a.time}Z`) - new Date(`${b.date}Т${b.time}`))[0];//Отсортировал по времени взял первую
                
                const countdownDiv = document.getElementById("next-gp-countdown");
                if (!nextSession){
                    countdownDiv.innerHTML = "<p>Нет ближайшей сессии</p>";
                    return;
                }

                updateCountdown(nextSession,countdownDiv);
                setInterval(() => updateCountdown(nextSession, countdownDiv), 60_000);
                
            });

    });
}


function loadDriverStandings() {
    Promise.all([
        fetch(`${API}/standings/drivers/?season=2026`).then(r => r.json()),
        fetch(`${API}/drivers/`).then(r => r.json())
    ]).then(([standings, drivers]) => {
        const driverMap = {};
        drivers.forEach(d => driverMap[d.id] = `${d.first_name} ${d.last_name} #${d.number}`);
        
        const content = document.getElementById("standings-content");
        content.innerHTML = "";
        standings.sort((a, b) => parseInt(a.position) - parseInt(b.position));
        standings.forEach(s => {
            const name = driverMap[s.driver_id] || `ID ${s.driver_id}`;
            const pos = parseInt(s.position);
            let medalClass = "";
            if (pos === 1) medalClass = "gold";
            else if (pos === 2) medalClass = "silver";
            else if (pos === 3) medalClass = "bronze";

            content.innerHTML += `
                <div class="card ${medalClass}">
                    <h3>${s.position}. ${name}</h3>
                    <p>${s.points} очков</p>
                </div>
            `;
        });
    });
}


function loadConstructorStandings() {
    Promise.all([ //Запускает несколько запросов одновременно
        fetch(`${API}/standings/constructors/?season=2026`).then(r => r.json()),
        fetch(`${API}/constructors/`).then(r => r.json())
    ]).then(([standings, constructors]) => {
        const constructorMap = {};// Cловарь
        constructors.forEach(c => constructorMap[c.id] = c.name); //Строит словарь id: name
        
        const content = document.getElementById("standings-content");
        content.innerHTML = "";
        standings.sort((a, b) => parseInt(a.position) - parseInt(b.position));
        standings.forEach(s => {
            const name = constructorMap[s.constructor_id] || `ID ${s.constructor_id}`; //Берем id команды и сопооставляем с именем
            const pos = parseInt(s.position);
            let medalClass = "";
            if (pos === 1) medalClass = "gold";
            else if (pos === 2) medalClass = "silver";
            else if (pos === 3) medalClass = "bronze";

            content.innerHTML += `
                <div class="card ${medalClass}">
                    <h3>${s.position}. ${name}</h3>
                    <p>${s.points} очков</p>
                </div>
            `;
        });
    });
}

function initDriverSort(){
    document.querySelectorAll("#drivers .standings-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll("#drivers .standings-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            if (btn.dataset.sort === "default"){
                driversData.sort((a, b) => a.id - b.id);
            }
            else if (btn.dataset.sort === "wins"){
                driversData.sort((a, b) => b.wins - a.wins);
            }
            else if (btn.dataset.sort === "podiums"){
                driversData.sort((a, b) => b.podiums - a.podiums);
            }

            renderDrivers(driversData);
        })
    })
}




function initStandingsSwitch(){
    document.querySelectorAll(".standings-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".standings-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            if (btn.dataset.standings === "drivers"){
                loadDriverStandings();
            }
            else {
                loadConstructorStandings();
            }
        })
    })
}


window.addEventListener("load", () => {
    loadNextGp();
});



document.querySelectorAll("nav button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll("nav button")
      .forEach((nb) => nb.classList.remove("active"));
    document
      .querySelectorAll(".tab-content")
      .forEach((tb) => tb.classList.remove("active"));

    btn.classList.add("active");

    document.getElementById(btn.dataset.tab).classList.add("active");

    if (btn.dataset.tab === "circuits") {
      loadCircuits();
    } else if (btn.dataset.tab === "drivers") {
      loadDrivers();
      initDriverSort();
    } else if (btn.dataset.tab === "constructors") {
      loadConstructors();
    } else if (btn.dataset.tab === "grandprix") {
      loadGrandprix();
    } else if (btn.dataset.tab === "standings"){
        loadDriverStandings();
        initStandingsSwitch();
    }
  });
});
