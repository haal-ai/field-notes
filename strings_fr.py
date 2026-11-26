"""Every reader-facing string of the generated site, in French, in one place.

Review wording here. build.py and assets/site.js read these values; nothing else
should hold visible text. Dates use the tables below, never the operating-system locale.
"""
from datetime import date

MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août',
          'septembre', 'octobre', 'novembre', 'décembre']
MONTHS_SHORT = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août',
                'sept.', 'oct.', 'nov.', 'déc.']


def fr_day(d):
    """25 nov. 2026 (1er déc. 2026 for the first of the month)."""
    return f'{"1er" if d.day == 1 else d.day} {MONTHS_SHORT[d.month - 1]} {d.year}'


def fr_month_year(d):
    """novembre 2026."""
    return f'{MONTHS[d.month - 1]} {d.year}'


# Catalogue section keys (as written in entries) -> displayed names. A French name in an entry passes through.
SECTION_NAMES = {
    'Inference': 'Inférence',
    'Evaluation': 'Évaluation',
    'About this library': 'À propos de la bibliothèque',
}
ABOUT = 'À propos de la bibliothèque'
SECTION_NOTES = {
    'Inférence': 'Comment les modèles fonctionnent : requêtes, mémoire, serveurs.',
    'Évaluation': 'Petits tests, avec leur protocole et leurs limites.',
    ABOUT: 'Comment lire ces notes.',
}
SECTION_NOTE_DEFAULT = 'Notes sur ce sujet : {name}.'

KIND = {'guide': 'GUIDE', 'news': 'ACTUALITÉ', 'experiment': 'EXPÉRIENCE'}

T = {
    # page shell
    'lang': 'fr',
    'site_name': 'HAAL',
    'brand_sub': 'NOTES DE TERRAIN D’INGÉNIERIE',
    'description': 'Des explications sur l’IA et l’ingénierie logicielle, avec dates, sources et figures utiles.',
    'skip': 'Aller au contenu',
    'nav_aria': 'Navigation principale',
    'nav_catalogue': 'Catalogue',
    'nav_glossary': 'Glossaire',
    'nav_archive': 'Archives',
    'nav_ledger': 'Suivi des relectures',
    'theme': 'Thème',
    'theme_system': 'système',
    'theme_dark': 'sombre',
    'theme_light': 'clair',
    'footer_brand': 'HAAL / NOTES DE TERRAIN',
    'footer_tagline': 'Notes pratiques sur l’IA et l’ingénierie logicielle, avec leurs dates',
    'footer_dates': 'Dates et durée de vie des contenus',
    'preview_title': '[Aperçu] {title}',
    'preview_banner': 'APERÇU PRIVÉ. Contient des brouillons non publiés et non approuvés. Ne jamais déployer cette version.',
    'noscript': '',
    # dates
    'undated': 'Défini à la publication',
    'updated': 'Mis à jour le {date}',
    'published_label': 'Publié',
    'published_on': 'Publié le',
    'edited_on': 'Modifié le',
    # catalogue
    'eyebrow': 'OPEN SOURCE · POIDS OUVERTS · INGÉNIERIE PRATIQUE',
    'hero': 'Comprendre.<br><span>Essayer. Documenter.</span>',
    'intro': 'L’IA et l’ingénierie logicielle, expliquées par des figures.<br>Chaque page indique ses dates et son état de relecture.',
    'notes_count': {'one': '{n} note', 'other': '{n} notes'},
    'start_title': 'Commencer par une explication',
    'start_hint': 'DES FIGURES, PEU DE TEXTE.',
    'featured_read': 'Lire l’explication',
    'featured_tag': 'ARTICLE + FIGURES',
    'browse_title': 'Parcourir les notes',
    'search_label': 'Rechercher dans les titres et les descriptions',
    'search_placeholder': 'Chercher une explication, une expérience ou un sujet…',
    'show_old_news': 'Afficher les anciennes actualités',
    'filter_aria': 'Type de contenu',
    'filter_all': 'Toutes les entrées',
    'filter_guide': 'Guides',
    'filter_experiment': 'Expériences',
    'filter_news': 'Actualités',
    'empty': 'Aucune entrée ne correspond. Essayez un autre filtre ou effacez la recherche.',
    'open_archive': 'Ouvrir les archives des actualités',
    'article_with_figures': 'Article avec figures',
    'of': 'sur',
    # sidebar
    'side_aria': 'Sections',
    'side_title': 'Sections',
    'side_all': 'Toutes les sections',
    # section cards (home) and section pages
    'browse_sections_title': 'Parcourir par section',
    'section_recent': 'Notes récentes',
    'section_view_all': 'Voir les {n} notes',
    'crumb_sections': 'Sections',
    'section_type_filter_aria': 'Filtrer les notes de cette section',
    'section_search_placeholder': 'Chercher dans cette section…',
    'section_page_of': 'Page {page} sur {total}',
    'section_prev': 'Page précédente',
    'section_next': 'Page suivante',
    'search_results_title': 'Résultats de recherche',
    'search_results_count': {'one': '{n} résultat', 'other': '{n} résultats'},
    'search_results_empty': 'Aucun résultat. Essayez un autre mot ou un autre filtre.',
    'search_results_hint': 'Tapez au moins deux lettres pour chercher dans toutes les sections.',
    # principles and about
    'principles_title': 'Utile aujourd’hui. Honnête sur le temps.',
    'principle_news_title': 'Une fenêtre de trois mois',
    'principle_news': 'Une observation datée. Après trois mois calendaires, elle passe aux archives avec un avis de péremption. La modifier ne relance pas le compteur.',
    'principle_guide_title': 'Un savoir à revisiter',
    'principle_guide': 'Une explication faite pour durer. Elle affiche sa dernière relecture et la date de la prochaine. Une relecture manquée signifie « à relire », pas « devenu faux ».',
    'principle_experiment_title': 'Des résultats liés à une configuration connue',
    'principle_experiment': 'La date du test, les versions, la méthode et les limites restent avec le résultat. Une ancienne mesure reste une trace historique ; elle ne décrit pas une version plus récente.',
    'about_label': 'À PROPOS DE LA BIBLIOTHÈQUE',
    'about_title': 'Un travail pratique,<br>avec son contexte.',
    'about_1': 'Ces notes partagent des explications et des expériences sur l’IA et l’ingénierie logicielle. Chaque page indique ses dates, ses sources et ses limites. Ce sont de simples partages, sans ambition scientifique.',
    'about_2': 'Aucun compte requis. Aucun compteur d’audience. Chaque page cite des sources publiques.',
    'about_3': 'Une date sur chaque page. Une limite claire pour chaque affirmation.',
    'choose_visual_title': 'Choisir un parcours de lecture',
    'choose_visual_nodes': ['Actualités', 'Guides', 'Expériences'],
    'choose_visual_details': ['Observations datées · trois mois', 'Explications durables · dates de relecture', 'Tests enregistrés · versions et limites'],
    'choose_visual_caption': 'Choisissez une actualité pour une information datée, un guide pour une explication, ou une expérience pour des preuves issues d’une configuration précise.',
    # statuses and actions
    'status_draft': 'Brouillon (non publié)',
    'action_draft': 'Relecture, contrôle des droits et approbation avant publication',
    'status_news_current': 'Actualité en cours',
    'status_news_old': 'Actualité ancienne',
    'action_news_old': 'Chercher une actualité plus récente',
    'action_news_current': 'Archiver l’actualité à l’échéance',
    'status_guide_ok': 'À jour · prochaine relecture {month}',
    'status_guide_due': 'À relire',
    'action_guide': 'Relecture',
    'status_experiment_dated': 'Expérience · testée le {date}',
    'status_experiment': 'Expérience',
    'action_experiment': 'Vérifier la pertinence ; conserver la mesure d’origine',
    # article page
    'crumb_catalogue': 'Catalogue',
        'meta_published': 'Première publication',
    'meta_edited': 'Dernière modification',
    'meta_reviewed': 'Dernière relecture',
    'meta_next': 'Prochaine relecture',
    'meta_expires': 'Expire le',
    'notice_news': 'Un compte rendu daté. Il passe aux archives après trois mois calendaires.',
    'notice_guide': 'Une date de relecture dépassée signifie que le guide est à relire. Cela ne prouve pas que le contenu est faux.',
    'notice_experiment': 'Ces résultats valent pour la configuration enregistrée. Vérifiez les versions et la date du test.',
    'notice_draft': 'Aperçu de brouillon. Non publié, non approuvé. Les dates sont fixées à la publication.',
    'notice_all': 'Cet article n\'a pas de valeur scientifique et n\'est pas la copie d\'une autre publication. Il n\'est pas contre-vérifié : c\'est un simple partage, sans ambition.',
    'history': 'Historique des révisions',
    'figure_text': 'Équivalent textuel de la figure',
    'figure_text_missing': 'L’équivalent textuel de cette figure n’est pas encore rédigé.',
    'figure_missing': 'Figure manquante : {name}',
    # ledger
    'ledger_eyebrow': 'SUIVI DES RELECTURES',
    'ledger_title': 'Ce qui doit être relu,<br><span>et quand.</span>',
    'ledger_intro': 'Calculé le {date} (UTC dans la build planifiée). Les dates viennent du catalogue de publication.',
    'ledger_queue': 'File de relecture',
    'ledger_row': '{action} · Échéance {due} · {status}',
    'ledger_download': 'Télécharger le suivi (JSON)',
    'ledger_title_short': 'Suivi des relectures',
    'ledger_visual_title': 'Décisions de relecture',
    'ledger_visual_nodes': ['Contrôler l’échéance', 'Relire le contenu et les sources', 'Consigner le résultat'],
    'ledger_visual_details': ['Un minuteur repère le travail', 'Une personne relit la page', 'Conserver les dates de relecture'],
    'ledger_visual_caption': 'La build quotidienne met à jour les dates affichées. Elle ne relit rien et n’approuve aucun contenu nouveau.',
    # archive
    'archive_title': 'Archives des actualités',
    'archive_intro': 'Les comptes rendus datés restent accessibles après la fin de leur période « en cours ».',
    'archive_policy': 'Règle d’archivage',
    'archive_none': 'Aucune actualité n’a encore atteint la limite de trois mois. La première expire le {date}.',
    'archive_visual_title': 'Les archives des actualités',
    'archive_visual_nodes': ['Compte rendu d’origine', 'Limite de trois mois', 'Référence historique'],
    'archive_visual_details': ['La première publication reste figée', 'L’actualité devient ancienne', 'À lire avec son contexte d’origine'],
    'archive_visual_caption': 'L’archivage change la présentation de l’actualité. Il conserve le compte rendu d’origine et sa date de publication.',
    # glossary
    'glossary_title': 'Glossaire',
    'glossary_intro': 'Les termes techniques restent en anglais, comme dans les documentations. Voici ce que chacun veut dire et où il est utilisé.',
    'glossary_visual_title': 'Comment lire un terme',
    'glossary_visual_nodes': ['Premier usage', 'Lien', 'Définition'],
    'glossary_visual_details': ['Dans un article, le terme est souligné', 'Un clic ouvre cette page', 'Une définition courte, et les articles concernés'],
    'glossary_visual_caption': 'Dans chaque article, la première mention d’un terme technique renvoie à sa définition ici.',
    # 404 and retired
    'notfound_title': 'Page introuvable',
    'notfound_h1': 'Cette page n’est pas dans le catalogue.',
    'open_catalogue': 'Ouvrir le catalogue',
    'retired_title': 'Page retirée',
    'retired_h1': 'Cette page a été retirée.',
}

# The strings site.js needs (theme button, counts, search). Sent to the page as JSON.
JS_KEYS = ('theme', 'theme_system', 'theme_dark', 'theme_light', 'of', 'notes_count',
           'search_results_title', 'search_results_count', 'search_results_empty', 'search_results_hint', 'nav_catalogue')
