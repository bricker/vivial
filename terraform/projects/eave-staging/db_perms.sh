user: postgres
db: postgres

grant "mb-xxx@eave-staging.iam" to postgres;
alter db "mb_xxx" owner to "mb-xxx@eave-staging.iam";
revoke "mb-xxx@eave-staging.iam" from postgres;