// =====================================================================================
// Power Query (M) - load the cleaned dataset produced by Python/run_pipeline.py
// Home > Get Data > Text/CSV > Transform Data > Advanced Editor > paste this query.
// Name the query: claims
// CHANGE the file path in `Source` to where you cloned the repository.
// =====================================================================================
let
    Source = Csv.Document(
        File.Contents("C:\Healthcare-Insurance-Claims-Analysis\Dataset\processed\claims_clean.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"record_id", Int64.Type},
            {"age", Int64.Type},
            {"sex", type text},
            {"bmi", type number},
            {"children", Int64.Type},
            {"smoker", type text},
            {"region", type text},
            {"charges", type number},
            {"age_group", type text},
            {"bmi_category", type text},
            {"has_children", type text},
            {"smoker_flag", Int64.Type},
            {"log_charges", type number},
            {"is_high_cost", type logical},
            {"is_iqr_outlier", type logical},
            {"charge_band", type text},
            {"smoker_bmi_segment", type text},
            {"peer_median_charge", type number},
            {"peer_upper_fence", type number},
            {"charge_vs_peer_median", type number},
            {"is_peer_anomaly", type logical},
            {"anomaly_direction", type text}
        },
        "en-US"
    ),

    // Friendly labels for visuals
    TitleCase = Table.TransformColumns(
        Typed,
        {{"sex", Text.Proper, type text}, {"region", Text.Proper, type text}}
    ),

    // Sort-order helper columns (use Column tools > Sort by column in the model view)
    AgeOrder = Table.AddColumn(
        TitleCase, "age_group_order",
        each List.PositionOf({"18-24", "25-34", "35-44", "45-54", "55-64"}, [age_group]) + 1,
        Int64.Type
    ),
    BmiOrder = Table.AddColumn(
        AgeOrder, "bmi_category_order",
        each List.PositionOf({"Underweight", "Normal", "Overweight", "Obese"}, [bmi_category]) + 1,
        Int64.Type
    ),
    BandOrder = Table.AddColumn(
        BmiOrder, "charge_band_order",
        each List.PositionOf({"<5K", "5K-10K", "10K-20K", "20K-40K", "40K+"}, [charge_band]) + 1,
        Int64.Type
    ),

    // Smoker label (the raw value is lowercase yes/no; DAX measures compare against "yes"/"no" on this column,
    // so keep `smoker` as-is and add a separate display column)
    SmokerLabel = Table.AddColumn(
        BandOrder, "smoker_label",
        each if [smoker] = "yes" then "Smoker" else "Non-smoker", type text
    )
in
    SmokerLabel
