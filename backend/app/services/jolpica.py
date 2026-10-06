import httpx
from sqlalchemy.orm import Session
from app import models


#Константы
JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"
SESSION_TYPES = {
    "FirstPractice": "fp1",
    "SecondPractice": "fp2",
    "ThirdPractice": "fp3",
    "Qualifying": "qualifying",
    "Sprint": "sprint",
    "SprintQualifying": "sprint_qualifying",
}

CONSTRUCTOR_MAP = {
    "mercedes": "Mercedes",
    "ferrari": "Ferrari",
    "red_bull": "Red Bull Racing",
    "mclaren": "McLaren",
    "aston_martin": "Aston Martin",
    "alpine": "Alpine",
    "williams": "Williams",
    "rb": "Racing Bulls",
    "audi": "Audi",
    "haas": "Haas",
    "cadillac": "Cadillac F1 Team",
}


def fetch_races(season: int) -> dict:
    url = f"{JOLPICA_BASE}/{season}.json"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    return response.json()


def load_season(season: int, db: Session) -> dict:
    data = fetch_races(season)
    races = data["MRData"]["RaceTable"]["Races"]

    stats = {"circuits": 0, "grandprix": 0, "sessions": 0}

    #ТРАССА
    for race in races:
        circuit_data = race["Circuit"]
        circuit_name = circuit_data["circuitName"]

        circuit = db.query(models.Circuit).filter(models.Circuit.name == circuit_name).first()

        if not circuit:
            circuit = models.Circuit(
                name = circuit_name,
                locality = circuit_data["Location"]["locality"],
                country = circuit_data["Location"]["country"],
            )

            db.add(circuit)
            db.flush() #Отправляет в бд но не фиксирует окончательно
            stats["circuits"] += 1


        #Гран-при
        gp = models.GrandPrix(
            season = season,
            round = int(race["round"]),
            name = race["raceName"],
            circuit_id = circuit.id,
            date = race["date"],
            time = race["time"].rstrip("Z")
        )
        db.add(gp)
        db.flush()
        stats["grandprix"] += 1


        for jolpica_key, session_type in SESSION_TYPES.items():
            if jolpica_key in race:
                session_data = race[jolpica_key]
                session = models.RaceSession(
                    grand_prix_id = gp.id,
                    type = session_type,
                    name = session_type.upper(),
                    date = session_data["date"],
                    time = session_data["time"].rstrip("Z"),
                )
                db.add(session)
                stats["sessions"] += 1

        race_session = models.RaceSession(
                    grand_prix_id = gp.id,
                    type = "race",
                    name = "RACE",
                    date = race["date"],
                    time = race["time"].rstrip("Z"),
                )
        db.add(race_session)
        stats["sessions"] += 1
         

    db.commit()
    return stats


def load_drivers(season: int, db: Session) -> dict:
    url = f"{JOLPICA_BASE}/{season}/drivers.json"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    drivers = data["MRData"]["DriverTable"]["Drivers"]
    stats = {"drivers": 0, "skipped": 0}

    for d in drivers:
        code = d.get("code")
        if not code:
            continue

        #Проверяем, есть ли уже
        existing = db.query(models.Driver).filter(models.Driver.code == code).first()

        if existing:
            stats["skipped"] += 1
            continue

        driver = models.Driver(
            first_name=d.get("givenName", ""),
            last_name=d.get("familyName", ""),
            nationality=d.get("nationality", ""),
            number=d.get("permanentNumber", ""),
            code=code,
        )
        db.add(driver)
        stats["drivers"] += 1
    
    db.commit()
    return stats


def load_driver_standings(season: int, db: Session) -> dict:
    url = f"{JOLPICA_BASE}/{season}/driverstandings.json"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    stats = {"standings": 0, "updated": 0, "skipped": 0}
    
    for s in standings:
        code = s["Driver"]["code"]
        driver = db.query(models.Driver).filter(models.Driver.code == code).first()
        
        if not driver:
            stats["skipped"] += 1
            continue
        
        existing = db.query(models.DriverStanding).filter(
            models.DriverStanding.season == season,
            models.DriverStanding.driver_id == driver.id
        ).first()
        
        if existing:
            #Обновляем данные(Если запись есть)
            existing.position = s["position"]
            existing.points = float(s["points"])
            stats["updated"] += 1
        else:
            #Создаем новую запись
            standing = models.DriverStanding(
                season=season,
                round=0,
                position=s["position"],
                driver_id=driver.id,
                points=float(s["points"]),
            )
            db.add(standing)
            stats["standings"] += 1
    
    db.commit()
    return stats


def load_constructors(season: int, db: Session) -> dict:
    url = f"{JOLPICA_BASE}/{season}/constructors.json"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    
    constructors = data["MRData"]["ConstructorTable"]["Constructors"]
    stats = {"constructors": 0, "skipped": 0}
    
    for c in constructors:
        jolpica_id = c["constructorId"]
        name = CONSTRUCTOR_MAP.get(jolpica_id, c["name"])
        
        existing = db.query(models.Constructor).filter(
            models.Constructor.name == name
        ).first()
        
        if existing:
            stats["skipped"] += 1
            continue
        
        constructor = models.Constructor(
            name=name,
            short_name=c.get("constructorId", "")[:3].upper(),
            country=c.get("nationality", ""),
        )
        db.add(constructor)
        stats["constructors"] += 1
    
    db.commit()
    return stats



def load_constructor_standings(season: int, db: Session) -> dict:
    url = f"{JOLPICA_BASE}/{season}/constructorstandings.json"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    stats = {"standings": 0, "updated": 0, "skipped": 0}

    for s in standings:
        jolpica_id = s["Constructor"]["constructorId"]
        name = CONSTRUCTOR_MAP.get(jolpica_id)

        if not name:
            stats["skipped"] += 1
            continue

        constructor = db.query(models.Constructor).filter(models.Constructor.name == name).first()

        if not constructor:
            stats["skipped"] += 1
            continue

        existing = db.query(models.ConstructorStanding).filter(
            models.ConstructorStanding.season == season,
            models.ConstructorStanding.constructor_id == constructor.id
        ).first()

        if existing:
            existing.position = s["position"]
            existing.points = float(s["points"])
            stats["updated"] += 1
        else:
            standing = models.ConstructorStanding(
                season=season,
                round=0,
                position=s["position"],
                constructor_id=constructor.id,
                points=float(s["points"]),
            )
            db.add(standing)
            stats["standings"] += 1

    db.commit()
    return stats


def load_qualifying(season: int, db: Session) -> dict:
    qualifying_sessions = db.query(models.RaceSession).filter(
        models.RaceSession.type == "qualifying"
    ).all()
    

    stats = {"qualifying": 0, "skipped": 0}
    

    for session in qualifying_sessions:
        gp = db.query(models.GrandPrix).filter(
            models.GrandPrix.id == session.grand_prix_id
        ).first()
        
        if not gp:
            continue

        print(f"Обрабатываю : {gp.name}, round={gp.round}")
        

        url = f"{JOLPICA_BASE}/{season}/{gp.round}/qualifying.json"
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        

        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            continue
        
        qualifying_data = races[0]["QualifyingResults"]
        
        for q in qualifying_data:

            code = q["Driver"]["code"]
            driver = db.query(models.Driver).filter(
                models.Driver.code == code
            ).first()
            
            if not driver:
                stats["skipped"] += 1
                continue
            
            jolpica_constructor = q["Constructor"]["constructorId"]
            constructor_name = CONSTRUCTOR_MAP.get(jolpica_constructor)

            
            if not constructor_name:
                stats["skipped"] += 1
                continue
            
            constructor = db.query(models.Constructor).filter(
                models.Constructor.name == constructor_name
            ).first()

            
            if not constructor:
                stats["skipped"] += 1
                continue
            

            existing = db.query(models.QualifyingResult).filter(
                models.QualifyingResult.session_id == session.id,
                models.QualifyingResult.driver_id == driver.id
            ).first()
            
            if existing:
                stats["skipped"] += 1
                continue
            

            result = models.QualifyingResult(
                session_id=session.id,              
                driver_id=driver.id,                 
                constructor_id=constructor.id,       
                position=q["position"],              
                q1=q.get("Q1"),                
                q2=q.get("Q2"),                
                q3=q.get("Q3"),                
            )
            db.add(result)
            stats["qualifying"] += 1
    
    db.commit()
    return stats




def load_results(season: int, db: Session) -> dict:
    # 1. Получаем ВСЕ сессии типа "race" из базы
    # У каждой гонки одна такая сессия типо гонка = сессия
    race_sessions = db.query(models.RaceSession).filter(
        models.RaceSession.type.in_(["race", "sprint"])
    ).all()
    
    # Счётчики для отчёта: сколько создали, сколько пропустили
    stats = {"results": 0, "sprint": 0, "skipped": 0}

    print(f"Всего сессий (race + sprint) : {len(race_sessions)}")
    
    # 2. Проходимся по каждой гонке сезона
    for session in race_sessions:
        # 2.1. Находим ГП этой сессии, чтобы узнать round(номер этапа)
        gp = db.query(models.GrandPrix).filter(
            models.GrandPrix.id == session.grand_prix_id
        ).first()
        
        if not gp:
            continue  # нет ГП — пропускаем (не должно быть)

        print(f"Обрабатываю : {gp.name}, round={gp.round} type={session.type}")
        
        # 3. Запрашиваем результаты конкретной гонки из Jolpica
        if session.type == "sprint":
            url = f"{JOLPICA_BASE}/{season}/{gp.round}/sprint.json"
            results_key = "SprintResults"
        else:
            url = f"{JOLPICA_BASE}/{season}/{gp.round}/results.json"
            results_key = "Results"
        
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            continue
        
        results_data = races[0][results_key]
        
        # 5. Проходимся по каждому пилоту в результатах
        for r in results_data:
            # 5.1. Сопоставляем пилота по code (RUS, VER)
            code = r["Driver"]["code"]
            driver = db.query(models.Driver).filter(
                models.Driver.code == code
            ).first()
            
            if not driver:
                # Пилота нет в базе — пропускаем
                stats["skipped"] += 1
                continue
            
            # 5.2. Сопоставляем команду через CONSTRUCTOR_MAP
            # Jolpica даёт constructorId="mercedes", у меня в базе name="Mercedes"
            jolpica_constructor = r["Constructor"]["constructorId"]
            constructor_name = CONSTRUCTOR_MAP.get(jolpica_constructor)
            
            if not constructor_name:
                # Нет в map — пропускаем
                stats["skipped"] += 1
                continue
            
            constructor = db.query(models.Constructor).filter(
                models.Constructor.name == constructor_name
            ).first()
            
            if not constructor:
                # Нет в базе — пропускаем
                stats["skipped"] += 1
                continue
            
            # 5.3. Проверяем, нет ли уже такой записи
            # Уникальность: session_id + driver_id(Пилот не может финишировать дважды в гонке)
            existing = db.query(models.Result).filter(
                models.Result.session_id == session.id,
                models.Result.driver_id == driver.id
            ).first()
            
            if existing:
                stats["skipped"] += 1
                continue
            
            # 5.4. Обрабатываем поле Time
            # У финишировавших — есть Time: {"time": "1:23:06.801"}
            # У DNF/DSQ — Time отсутствует
            time_str = None
            if "Time" in r:
                time_str = r["Time"]["time"]
            
            # 5.5. Обрабатываем FastestLap (быстрый круг)
            # Он только у ОДНОГО пилота за гонку — rank == "1"
            fastest = False
            if "FastestLap" in r and r["FastestLap"].get("rank") == "1":
                fastest = True
            
            # 5.6. Создаём запись Result
            result = models.Result(
                session_id=session.id,              # FK → sessions
                driver_id=driver.id,                 # FK → drivers
                constructor_id=constructor.id,       # FK → constructors
                position=r["position"],              # строка "1", "2", ...
                grid=int(r["grid"]) if r["grid"] else None,    # стартовая позиция
                laps=int(r["laps"]) if r["laps"] else None,    # сколько кругов
                points=float(r["points"]),           # "25" → 25.0
                time=time_str,                       # "1:23:06.801" или "+2.974"
                status=r["status"],                  # "Finished", "Retired", "Lapped"
                fastest_lap=fastest,                 # True/False
            )
            db.add(result)
            if session.type == "sprint":
                stats["sprint"] += 1
            else:
                stats["results"] += 1
    
    # 6. Один коммит в конце — все изменения сразу
    db.commit()
    return stats

