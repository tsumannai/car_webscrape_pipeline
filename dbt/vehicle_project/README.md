### Vehicle Project DBT

This dbt repository stores `vehicle_project` dbt project with `car_models` model. `car_models` is the model that transforms json files (raw webscraped data) into a vehicle features table.


Bronze layer: Raw data from json files that have been appended to from webscrapes.

Silver layer: From the raw data, the latest webscraped record of each car model is obtained and some data cleaning is performed.These are for users that want to find car features in a flat dimensional structure.

Gold Layer: The gold layer takes cleaned dimensional data, reconciles and transform them for analytics applications.

Test Layer: Aside from calling packaged tests (e.g dbt utils, great expectations...) inside the yml of each model file, there is a place to construct tests in SQL. A model can also be create to monitor the output of our tests to see if results align with our assumptions about the data.

### DBT Local Set up

After dbt has been installed locally. `.dbt/profiles.yml` may need to be changed. Here is an example below of what that should look like:

```
vehicle_project:
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 1

    prod:
      type: duckdb
      path: prod.duckdb
      threads: 4

  target: dev
```