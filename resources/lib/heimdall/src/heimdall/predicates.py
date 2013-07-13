from collections import namedtuple

def PredicateBuilder(short, namespace, properties):
    predicate = namedtuple(short, properties + [ "xmlns" ])
    predicate.xmlns = namespace

    for prop in properties:
        setattr(predicate, prop, namespace + prop)

    return predicate

# Good but needed?
rdf = PredicateBuilder("rdf", "http://www.w3.org/TR/rdf-schema/", [ "Class" ])

# Certain
dc = PredicateBuilder("dc", "http://purl.org/dc/elements/1.1/", [ "title", "creator", "description", "type", "format", "identifier", "date" ])
owl = PredicateBuilder("owl", "http://www.w3.org/2002/07/owl#", [ "sameAs", "differentFrom" ])
foaf = PredicateBuilder("foaf", "http://xmlns.com/foaf/spec/", [ "Agent", "Group", "Organization", "Person", "Document", "Image", "thumbnail", "homepage" ])

# Uncertain
media = PredicateBuilder("media", "http://purl.org/media#", [ "duration", "rating" ])
video = PredicateBuilder("video", "http://purl.org/video#", [ ])
audio = PredicateBuilder("audio", "http://purl.org/audio#", [ ])
# SWO_0000396: software developer organization
# SWO_0000397: software publisher organization
swo = PredicateBuilder("swo", "http://www.ebi.ac.uk/efo/swo", [ "SWO_0000396", "SWO_0000397" ])
# data_3106: System metadata <http://bioportal.bioontology.org/ontologies/49579/?p=terms&conceptid=data_3106>
edamontology = PredicateBuilder("edamontology", "http://edamontology.org/", [ "data_3106" ])

upnp = PredicateBuilder("upnp", "urn:schemas-upnp-org:metadata-1-0/upnp/", [ "artist", "album", "originalTrackNumber" ])
