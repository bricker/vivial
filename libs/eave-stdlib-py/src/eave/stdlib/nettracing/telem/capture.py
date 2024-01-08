"""
so are we going to basically end up writing our own open telem api interface impl??

curernt open telem impls predictably only capture url and http method

i think well need to fork every opentelem instrumetation rerpo we care about, alter code to gather req/resp body data, bundle our fork w/ the opentelem api, and then release for customers
(unsure if there is a 1 LOC solution for opentelem; current demo was wrapping the executable)
"""