from django.shortcuts import render, get_object_or_404, redirect
from .models import Pays, Titre
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton

def accueil(request):
    return render(request, 'mon_app/accueil.html')

def select_pays(request):
    pays_list = Pays.objects.all().order_by('nom')
    return render(request, 'mon_app/select_pays.html', {
        'pays_list': pays_list,
    })

def get_titres_data(request):
    pays_code = request.GET.get('pays')
    type_titre = request.GET.get('type_titre')
    
    titres = Titre.objects.filter(pays__nom=pays_code)
    if type_titre:
        titres = titres.filter(type_titre=type_titre)
    
    data = {
        'types_titres': list(titres.values_list('type_titre', flat=True).distinct()),
        'titres': list(titres.values('isin', 'denomination'))
    }
    return JsonResponse(data)

def isin_list(request):
    pays_code = request.GET.get('pays_code')
    type_titre = request.GET.get('type_titre')
    isin = request.GET.get('isin')
    
    if isin:
        return redirect('titre_detail', isin=isin)
    
    try:
        pays = Pays.objects.get(nom=pays_code)
    except Pays.DoesNotExist:
        messages.error(request, "Pays non trouvé")
        return redirect('select_pays')
    
    titres = Titre.objects.filter(pays=pays)
    if type_titre:
        titres = titres.filter(type_titre=type_titre)
    
    return render(request, 'mon_app/isin_list.html', {
        'pays': pays,
        'titres': titres,
        'type_titre_selectionne': type_titre,
    })



from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton
import logging

logger = logging.getLogger(__name__)

def parse_date(date_str):
    """Convertit une chaîne 'JJ/MM/AAAA' en objet date"""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None

def titre_detail(request, isin):
    try:
        titre = get_object_or_404(Titre.objects.select_related('pays'), isin=isin)
        
        # Conversion des dates
        date_valeur = parse_date(titre.date_valeur) if isinstance(titre.date_valeur, str) else titre.date_valeur
        
        # Validation des données essentielles
        if None in [date_valeur, titre.valeur_nominale, titre.taux_interet, titre.duree]:
            messages.error(request, "Données incomplètes - impossible d'effectuer les calculs")
            return render(request, 'mon_app/titre_detail.html', {'titre': titre})

        try:
            # Conversion des valeurs numériques
            prix_pondere = float(titre.prix_pondere) if titre.prix_pondere else float(titre.valeur_nominale)
            montant_restant = float(titre.valeur_nominale)
            taux_periodique = float(titre.taux_interet) / 100
            maturite = int(titre.duree)
            annees_differe = int(titre.annees_differe) if titre.annees_differe else 0
            type_amortissement = titre.type_amortissement.lower()
        except (ValueError, TypeError) as e:
            logger.error(f"Erreur conversion données : {str(e)}")
            messages.error(request, "Erreur dans le format des données numériques")
            return render(request, 'mon_app/titre_detail.html', {'titre': titre})

        # Détails du titre
        details = {
            'Pays': titre.pays.get_nom_display(),
            'Type de titre': titre.get_type_titre_display(),
            'ISIN': titre.isin,
            'Dénomination': titre.denomination,
            'Adjudication': titre.adjudication,
            'Durée': f"{maturite} ans",
            'Date de valeur': date_valeur.strftime("%d/%m/%Y") if date_valeur else "Date invalide",
            'Valeur nominale': f"{montant_restant:,.2f} XOF",
            'Taux d\'intérêt': f"{titre.taux_interet}%",
            'Type d\'amortissement': titre.get_type_amortissement_display(),
            'Années différées': f"{annees_differe}",
            'Prix pondéré': f"{prix_pondere:,.2f} XOF",
            'Taux coupon couru': f"{titre.taux_coupon_couru}%" if titre.taux_coupon_couru else "N/A"
        }

        # Initialisation des calculs
        tableau = []
        cash_flows = [-prix_pondere]
        dates = [date_valeur] if date_valeur else []
        
        if not date_valeur:
            messages.error(request, "Date de valeur manquante ou invalide")
            return render(request, 'mon_app/titre_detail.html', {
                'titre': titre,
                'details': details,
                'tableau': [],
                'rendement': None
            })

        # Ajout de la période 0 (investissement initial)
        tableau.append({
            'periode': 0,
            'date': date_valeur.strftime('%d/%m/%Y'),
            'montant_debut': '-',
            'interet': '-',
            'amortissement': '-',
            'annuite': f"{-prix_pondere:,.2f}",
            'montant_fin': "-"
        })

        try:
            # Construction du tableau d'amortissement
            if type_amortissement == 'in fine':
                for annee in range(1, maturite + 1):
                    date_paiement = date_valeur + relativedelta(years=annee)
                    interet = montant_restant * taux_periodique
                    
                    if annee == maturite:
                        amortissement = montant_restant
                        payment = interet + amortissement
                        
                    else:
                        payment = interet
                        amortissement = 0
                    
                    tableau.append({
                        'periode': annee,
                        'date': date_paiement.strftime('%d/%m/%Y'),
                        'montant_debut': f"{montant_restant:,.2f}",
                        'interet': f"{interet:,.2f}",
                        'amortissement': f"{amortissement:,.2f}",
                        'annuite': f"{payment:,.2f}",
                        'montant_fin': f"{montant_restant - amortissement:,.2f}"
                    })
                    cash_flows.append(payment)
                    dates.append(date_paiement)

            elif type_amortissement in ['lineaire', 'differe']:
                try:
                    amortissement_const = montant_restant / max(maturite - annees_differe, 1) if type_amortissement == 'differe' else montant_restant / maturite
                except ZeroDivisionError:
                    messages.warning(request, "La durée du titre est invalide pour le calcul")
                    amortissement_const = 0

                for periode in range(1, maturite + 1):
                    date_paiement = date_valeur + relativedelta(years=periode)
                    interet = montant_restant * taux_periodique
                    
                    if type_amortissement == 'differe' and periode <= annees_differe:
                        amortissement = 0
                    else:
                        amortissement = amortissement_const
                    
                    payment = interet + amortissement
                    tableau.append({
                        'periode': periode,
                        'date': date_paiement.strftime('%d/%m/%Y'),
                        'montant_debut': f"{montant_restant:,.2f}",
                        'interet': f"{interet:,.2f}",
                        'amortissement': f"{amortissement:,.2f}",
                        'annuite': f"{payment:,.2f}",
                        'montant_fin': f"{montant_restant - amortissement:,.2f}"
                    })
                    cash_flows.append(payment)
                    dates.append(date_paiement)
                    montant_restant -= amortissement

            # Calcul du rendement
            rendement = None
            if len(dates) > 1 and len(cash_flows) > 1:
                try:
                    def npv(rate):
                        days = [(date - dates[0]).days for date in dates]
                        return sum(
                            cf / (1 + rate) ** (day / 365.25)
                            for cf, day in zip(cash_flows, days)
                        )
                    
                    for guess in [0.05, 0.10, 0.01, 0.20]:
                        try:
                            rendement = round(newton(npv, guess, maxiter=50) * 100, 2)
                            break
                        except Exception as e:
                            logger.warning(f"Essai taux {guess} échoué: {str(e)}")
                            continue
                    
                    if rendement is None:
                        messages.warning(request, "Le calcul du rendement n'a pas convergé")
                except Exception as e:
                    logger.error(f"Erreur calcul rendement: {str(e)}")
                    messages.warning(request, "Erreur technique dans le calcul du rendement")

        except Exception as e:
            logger.error(f"Erreur calculs financiers: {str(e)}")
            messages.error(request, "Erreur dans les calculs financiers")
            tableau = []

        return render(request, 'mon_app/titre_detail.html', {
            'titre': titre,
            'details': details,
            'tableau': tableau,
            'rendement': rendement,
        })

    except Exception as e:
        logger.critical(f"Erreur vue titre_detail: {str(e)}")
        messages.error(request, "Une erreur technique est survenue")
        return render(request, 'mon_app/error.html', status=500)