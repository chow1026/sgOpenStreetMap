# To experiment with this code freely you will have to run this code locally.
# Take a look at the main() function for an example of how to use the code.
# We have provided example json output in the other code editor tabs for you to
# look at, but you will not be able to run any queries through our UI.
import json
import requests


BASE_URL = "http://musicbrainz.org/ws/2/"
ARTIST_URL = BASE_URL + "artist/"

# query parameters are given to the requests.get function as a dictionary; this
# variable contains some starter parameters.
query_type = {  "simple": {},
                "atr": {"inc": "aliases+tags+ratings"},
                "aliases": {"inc": "aliases"},
                "releases": {"inc": "releases"}}


def query_site(url, params, uid="", fmt="json"):
    # This is the main function for making queries to the musicbrainz API.
    # A json document should be returned by the query.
    params["fmt"] = fmt
    r = requests.get(url + uid, params=params)
    print("requesting", r.url)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def query_by_name(url, params, name):
    # This adds an artist name to the query parameters before making
    # an API call to the function above.
    params["query"] = "artist:" + name
    return query_site(url, params)


def pretty_print(data, indent=4):
    # After we get our output, we can format it to be more readable
    # by using this function.
    if type(data) == dict:
        print(json.dumps(data, indent=indent, sort_keys=True))
    else:
        print(data)


def main():
    '''
    Modify the function calls and indexing below to answer the questions on
    the next quiz. HINT: Note how the output we get from the site is a
    multi-level JSON document, so try making print statements to step through
    the structure one level at a time or copy the output to a separate output
    file.
    '''
    print('\nFIRST AID KIT QUERY')
    results = query_by_name(ARTIST_URL, query_type["simple"], "First Aid Kit")
    pretty_print(results)
    print('\nFirst Aid Kit Results Count: ', len(results["artists"]))

    # print('\nQUEEN QUERY')
    # results = query_by_name(ARTIST_URL, query_type["simple"], "Queen")
    # pretty_print(results)
    # print('\nQUEEN BEGING AREA QUERY')
    # artist_id = results["artists"][0]["id"]
    # begin_area_name = results["artists"][0]["begin-area"]["name"]
    # print("\nARTIST BEGIN AREA:", begin_area_name)
    # # pretty_print(results["artists"][0])
    #
    # print('\nBEATLES QUERY')
    # results = query_by_name(ARTIST_URL, query_type["simple"], "Beatles")
    # pretty_print(results)
    # artist_id = results["artists"][0]["id"]
    # alias_results = query_by_name(ARTIST_URL, query_type["aliases"], "Beatles")
    # pretty_print(alias_results)
    # alias_name = results["artists"][0]["aliases"][8]["name"]
    # print('\nBEATLES ALIAS NAME: ', alias_name)
    #
    # print('\nNIRVANA QUERY')
    # results = query_by_name(ARTIST_URL, query_type["simple"], "Nirvana")
    # pretty_print(results)
    # artist_disambiguation = results["artists"][0]["disambiguation"]
    # print('\nNIRVANA Disambiguation: ', artist_disambiguation)

    print('\nONE DIRECTION QUERY')
    one_dir_results = query_by_name(ARTIST_URL, query_type["simple"], "One Direction")
    pretty_print(one_dir_results)
    artist_formation_date = one_dir_results["artists"][0]["life-span"]['begin']
    print('\nONE DIRECTION Formed: ', artist_formation_date)

    # artist_data = query_site(ARTIST_URL, query_type["releases"], artist_id)
    # releases = artist_data["releases"]
    # print("\nONE RELEASE:")
    # pretty_print(releases[0], indent=2)
    # release_titles = [r["title"] for r in releases]
    #
    # print("\nALL TITLES:")
    # for t in release_titles:
    #     print(t)


if __name__ == '__main__':
    main()
