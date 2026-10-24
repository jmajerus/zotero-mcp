"""CSL name roles import as creator types the Zotero item type accepts.

Only author, editor, and translator were read, so a film's ``director``
was dropped; and an ``author`` on a film -- not a film creator type -- made
Zotero reject the item. Roles are now checked against the item type's
creator types (the API lists the primary one first).
"""

from zotero_mcp.citation_import import csl_json_to_zotero

CREATOR_TYPES = {
    "film": ["director", "castMember", "contributor", "producer", "scriptwriter"],
    "book": ["author", "contributor", "editor", "seriesEditor", "translator"],
    "bookSection": ["author", "bookAuthor", "contributor", "editor", "seriesEditor", "translator"],
}


def _template(zot_type):
    return {"itemType": zot_type, "title": "", "creators": [], "date": ""}


def _creator_types(zot_type):
    return [{"creatorType": t} for t in CREATOR_TYPES[zot_type]]


def _roles(csl, creator_types_fn=_creator_types):
    item = csl_json_to_zotero(csl, _template, creator_types_fn)
    return [(c["creatorType"], c.get("lastName") or c.get("name")) for c in item["creators"]]


def test_film_director_kept():
    csl = {"type": "motion_picture", "title": "Requiem for the American Dream",
           "director": [{"family": "Hutchison", "given": "Peter D."}, {"family": "Nyks", "given": "Kelly"}]}
    assert _roles(csl) == [("director", "Hutchison"), ("director", "Nyks")]


def test_author_becomes_primary_creator_type():
    csl = {"type": "motion_picture", "title": "Film", "author": [{"family": "Scott", "given": "Jared P."}]}
    assert _roles(csl) == [("director", "Scott")]


def test_role_invalid_for_type_becomes_contributor():
    csl = {"type": "book", "title": "Book", "author": [{"family": "Berlin", "given": "Isaiah"}],
           "director": [{"literal": "Someone"}]}
    assert _roles(csl) == [("author", "Berlin"), ("contributor", "Someone")]


def test_container_author_is_book_author():
    csl = {"type": "chapter", "title": "Chapter", "author": [{"family": "Winnicott", "given": "D. W."}],
           "container-author": [{"family": "Khan", "given": "M. Masud R."}]}
    assert _roles(csl) == [("author", "Winnicott"), ("bookAuthor", "Khan")]


def test_without_creator_types_old_roles_pass_through():
    csl = {"type": "motion_picture", "title": "Film", "author": [{"family": "Scott", "given": "Jared P."}],
           "director": [{"family": "Nyks", "given": "Kelly"}]}
    assert _roles(csl, None) == [("author", "Scott"), ("contributor", "Nyks")]
    assert _roles(csl, lambda zot_type: None) == [("author", "Scott"), ("contributor", "Nyks")]
