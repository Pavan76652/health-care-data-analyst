// Power Query M — Load fact_admissions from CSV
// Power BI Desktop: Home > Transform Data > New Source > Blank Query > Advanced Editor

let
    Source = Csv.Document(
        File.Contents("C:\path\to\healthcare-readmission-system\dashboard\data\fact_admissions.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"admission_id", Int64.Type},
        {"patient_id", Int64.Type},
        {"age_midpoint", Int64.Type},
        {"time_in_hospital", Int64.Type},
        {"num_medications", Int64.Type},
        {"readmitted_30_days", Int64.Type},
        {"admission_date", type date},
        {"admission_year", Int64.Type},
        {"admission_month", Int64.Type}
    }),
    AddedReadmitLabel = Table.AddColumn(ChangedTypes, "Readmitted", each if [readmitted_30_days] = 1 then "Yes" else "No")
in
    AddedReadmitLabel
