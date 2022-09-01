from rapidfuzz import fuzz
from rapidfuzz import process


def extract_from_list(
    argument,
    list_of_items,
    processors,
    score_cutoff=80,
    scorers=None,
):
    """Uses multiple scorers and processors for a good mix of accuracy and fuzzy-ness"""
    if scorers is None:
        scorers = [fuzz.WRatio]
    combined_list = []

    for scorer in scorers:
        for processor in processors:
            if fuzzy_list := process.extract(
                argument,
                list_of_items,
                scorer=scorer,
                processor=processor,
                score_cutoff=score_cutoff,
            ):
                combined_entries = [e[0] for e in combined_list]

                if (
                    processor == fuzz.WRatio
                ):  # WRatio isn't the best, so we add in extra filters to make sure everythings turns out ok
                    new_members = [
                        e
                        for e in fuzzy_list
                        if e[0] not in combined_entries
                        and (len(processor(e[0])) >= 2 or len(argument) <= 2)
                    ]

                else:
                    new_members = [
                        e for e in fuzzy_list if e[0] not in combined_entries
                    ]

                combined_list.extend(new_members)

    return combined_list
