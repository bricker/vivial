grant "gsa-app-mb-xxx@eave-staging.iam" to postgres;
alter database "mb_xxx" owner to "gsa-app-mb-xxx@eave-staging.iam";
revoke "gsa-app-mb-xxx@eave-staging.iam" from postgres;