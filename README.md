L'objectif de cette section est : 
De créer un algorithme python dans visual studio (avec si besoin plusieurs fichiers et librairies) me permettant de lancer automatiquement plusieurs optimisations de paramètres d'Experts sur Métatrader 5 sur plusieurs périodes (court terme, long terme...). 

En entrée l'algorithme prendra tout d'abord le lien vers le logiciel MT5 sur mon bureau ("C:\Program Files\IC Trading (MU) MT5 Terminal\terminal64.exe") lui donner les possibilités de robot que j'ai sur mt5, sur quel symbole, unité de temps, effet de levier, modèle, capital, timeframe etc... Lui donner le fichier d'optimisation .set correspondant, les différentes périodes de temps (courts termes et long termes avec backtest et forward test). 

Il lancera automatiquement alors MT5 puis refermera MT5 au fur et à mesure que les optimisations s'enchaineront. L'optimisation pourra être rapide (avec algorithme génétique ) ou lente en cas par cas. 

Tous les cas seront alors enregistrés dans un dossier pour chaque période (en backtest et forwardtest).

On fera alors un deuxieme algorithme pour post traiter les resultats. Il faudra ainsi trouver tous les passages avec des combinaisons interessantes. Il faudra analyser pourquoi ces combinaisons sont interessantes avec par exemple la volonté d'avoir toujours un DD max inferieur à 25%, des durées de positions maximale et moyenne pour chaque timeframe et passage, des objectifs de rendements par mois, des graphiques permettant de voir l'importance de tel ou tel paramètre. 

En + pq pas une interface IA me permettant de donner des caractéristiques de robots et des objectifs de résultats pour générer automatiquement des robots et de l'analyser (à faire plus tard)
En ++ Faire une interface qui prend en entrée un robot et qui automatiquement prend un robot sur MQL4 et l'analyse avec pleins de générations et nous permet de générer automatiquement une documentation claire sur le robot. (à faire plus tard)

mt5_automatic_optimizer/
│
├── config/
│   └── optimization_config.json     # Paramètres pour les runs (robots, symboles, .set, périodes, etc.)
│
├── optim/
│   └── mt5_launcher.py              # Lancement automatique de MT5 + optimisation
│   └── optimizer.py                 # Classe pour lancer l’optimisation d’un EA
│
├── analysis/
│   └── results_parser.py           # Extraction des résultats .xml/.html/.csv
│   └── analyzer.py                 # Analyse (drawdown, rendement, durée moy., importance paramètres…)
│
├── results/
│   ├── EURUSD_H1_Backtest/
│   ├── EURUSD_H1_Forwardtest/
│   └── ...
│
├── main.py                         # Script principal : orchestrateur
└── README.md
