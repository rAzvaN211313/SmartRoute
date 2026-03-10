SmartRoute AI - Sinteză Funcțională și Arhitectură
Aplicația reprezintă un sistem inteligent de monitorizare a flotei (Fleet Management System) care utilizează un algoritm de învățare pentru optimizarea timpilor de sosire (ETA), bazându-se pe analiza comportamentului istoric al șoferilor.
1. Operations Control (Monitorizare în timp real)
•	Funcționalitate: Reprezintă panoul principal de comandă unde sunt vizualizate unitățile de transport active pe harta interactivă.
•	Batch Deployment: Permite lansarea simultană a tuturor misiunilor planificate, optimizând procesul de expediție.
•	Telemetry Log: Un jurnal de sistem care înregistrează în timp real coordonatele geografice și evenimentele operaționale.
•	Validation (Arrived): La finalizarea cursei, sistemul compară timpul estimat inițial cu timpul real de parcurs pentru a genera date de antrenare pentru algoritmul AI.
2. Personnel Mgmt (Managementul Resurselor Umane)
•	Profilare Driver: Gestiunea bazei de date a șoferilor, unde fiecare profil deține un „Efficiency Factor” (coeficient de performanță).
•	AI Weighting: Acest factor este dinamic. Dacă un șofer înregistrează întârzieri sistematice, sistemul îi ajustează automat ponderea (ex: de la 1.0 la 1.2), astfel încât viitoarele planificări să fie mult mai realiste.
3. Fleet Assets (Managementul Flotei)
•	Gestiune Unități: Administrarea parcului auto (specific pe modele Volvo FH/FMX).
•	Data Integrity: Sistemul include un protocol de validare care previne duplicarea numerelor de înmatriculare în baza de date și asigură consistența datelor tehnice.
4. Dispatch Plan (Planificare Operațională)
•	Misiuni: Modulul de atribuire a resurselor. Dispecerul corelează un șofer disponibil cu un vehicul și o rută specifică.
•	In-Transit Logic: Implementează o regulă de business critică: șoferii și vehiculele aflate deja în cursă sunt marcate automat ca „In Transit” și devin indisponibile pentru noi misiuni până la finalizarea traseului curent.
5. Analytics Engine (Motorul de Învățare)
•	Machine Learning Evidence: Aceasta este componenta analitică a proiectului. Aici se generează grafice de performanță care demonstrează procesul de învățare al sistemului.
•	Rezultat: Graficul urmărește scăderea marjei de eroare (Error Margin) pe măsură ce sistemul colectează mai multe date, demonstrând creșterea preciziei predictive a platformei SmartRoute
