from datetime import date, timedelta
from scipy.optimize import newton

def calculer_amortissement(nominal, taux, duree, prix, differe):
    """Calcule le tableau d'amortissement et le rendement"""
    # Validation
    if any(v <= 0 for v in [nominal, taux, duree, prix]) or differe < 0:
        raise ValueError("Paramètres invalides")
    if differe >= duree:
        raise ValueError("La période de différé doit être inférieure à la maturité")

    # Initialisation
    tableau = []
    cashflows = [-prix]
    dates = [date.today()]
    amort_annuel = nominal / (duree - differe)
    capital_restant = nominal

    # Construction du tableau
    for annee in range(1, duree + 1):
        date_paiement = date.today() + timedelta(days=365*annee)
        interet = capital_restant * taux
        amort = amort_annuel if annee > differe else 0
        annuite = interet + amort
        
        ligne = {
            'annee': annee,
            'date': date_paiement.strftime("%d/%m/%Y"),
            'capital_debut': round(capital_restant, 2),
            'interet': round(interet, 2),
            'amortissement': round(amort, 2),
            'annuite': round(annuite, 2),
            'capital_fin': round(capital_restant - amort, 2)
        }
        
        tableau.append(ligne)
        cashflows.append(annuite)
        dates.append(date_paiement)
        capital_restant -= amort

    # Calcul du TRI
    try:
        tri = round(calculer_tri(cashflows, dates) * 100, 2)
    except:
        tri = None

    return {
        'tableau': tableau,
        'tri': tri,
        'parametres': {
            'nominal': nominal,
            'taux_annuel': taux * 100,
            'duree': duree,
            'prix_achat': prix,
            'annees_differe': differe
        }
    }

def calculer_tri(cashflows, dates):
    """Calcule le taux de rendement interne"""
    def npv(rate):
        return sum(
            cf / (1 + rate)**((date - dates[0]).days / 365)
            for cf, date in zip(cashflows, dates)
        )
    return newton(npv, 0.05, maxiter=100)