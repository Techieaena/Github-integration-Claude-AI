[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared #"AdventureWorks_Product_Categories csv" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Files", ItemKind = "Folder"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Name = "DatafolderAdventureWorks_Product_Categories"]}[Content],
  #"Navigation 4" = #"Navigation 3"{[Name = "AdventureWorks_Product_Categories.csv"]}[Content],
  #"Imported CSV" = Csv.Document(#"Navigation 4", [Delimiter = ",", Columns = 2, QuoteStyle = QuoteStyle.None]),
  #"Promoted headers" = Table.PromoteHeaders(#"Imported CSV", [PromoteAllScalars = true]),
  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"ProductCategoryKey", Int64.Type}, {"CategoryName", type text}})
in
  #"Changed column type";
shared #"duct_Subcategories csv" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Files", ItemKind = "Folder"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Name = "DatafolderProduct_Subcategories"]}[Content],
  #"Navigation 4" = #"Navigation 3"{[Name = "duct_Subcategories.csv"]}[Content],
  #"Imported CSV" = Csv.Document(#"Navigation 4", [Delimiter = ",", Columns = 3, QuoteStyle = QuoteStyle.None]),
  #"Promoted headers" = Table.PromoteHeaders(#"Imported CSV", [PromoteAllScalars = true]),
  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"ProductSubcategoryKey", Int64.Type}, {"SubcategoryName", type text}, {"ProductCategoryKey", Int64.Type}})
in
  #"Changed column type";
shared Merge = let
  Source = Table.NestedJoin(#"duct_Subcategories csv", {"ProductCategoryKey"}, #"AdventureWorks_Product_Categories csv", {"ProductCategoryKey"}, "AdventureWorks_Product_Categories csv", JoinKind.LeftOuter),
  #"Expanded AdventureWorks_Product_Categories csv" = Table.ExpandTableColumn(Source, "AdventureWorks_Product_Categories csv", {"ProductCategoryKey", "CategoryName"}, {"ProductCategoryKey.1", "CategoryName"}),
  #"Inserted conditional column" = Table.AddColumn(#"Expanded AdventureWorks_Product_Categories csv", "customkey", each if [ProductCategoryKey] = 1 then "One" else if [ProductSubcategoryKey] = 2 then "Two" else "Three")
in
  #"Inserted conditional column";
shared product = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "product", ItemKind = "Table"]}[Data],
  #"Changed column type" = Table.TransformColumnTypes(#"Navigation 2", {{"ProductKey", Int64.Type}, {"ProductSubcategoryKey", Int64.Type}, {"ProductCost", Int64.Type}, {"ProductPrice", type number}}),
  #"Added custom" = Table.AddColumn(#"Changed column type", "Main Model", each Text.Trim(Text.BeforeDelimiter([ModelName], ",")))
in
  #"Added custom";
shared calendar = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "calendar", ItemKind = "Table"]}[Data],
  #"Changed column type" = Table.TransformColumnTypes(#"Navigation 2", {{"Date", type date}}),
  #"Removed blank rows" = Table.SelectRows(#"Changed column type", each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null})))
in
  #"Removed blank rows";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "returndelta_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared returndelta = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "returndelta", ItemKind = "Table"]}[Data],
  #"Changed column type" = Table.TransformColumnTypes(#"Navigation 2", {{"ReturnDate", type date}, {"TerritoryKey", Int64.Type}, {"ProductKey", Int64.Type}, {"ReturnQuantity", Int64.Type}}),
  #"Inserted Month Name" = Table.AddColumn(#"Changed column type", "Month Name", each Date.MonthName([ReturnDate]), type text),
  #"Inserted Month" = Table.AddColumn(#"Inserted Month Name", "Month", each Date.Month([ReturnDate]), Int64.Type)
in
  #"Inserted Month";
shared sales = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "sales", ItemKind = "Table"]}[Data],
  #"Changed column type" = Table.TransformColumnTypes(#"Navigation 2", {{"OrderDate", type date}, {"StockDate", type date}, {"ProductKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"TerritoryKey", Int64.Type}, {"OrderLineItem", Int64.Type}, {"OrderQuantity", Int64.Type}})
in
  #"Changed column type";
shared subcat = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "subcat", ItemKind = "Table"]}[Data]
in
  #"Navigation 2";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "customers_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared customers = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "customers", ItemKind = "Table"]}[Data],
  #"Removed errors" = Table.RemoveRowsWithErrors(#"Navigation 2", {"Prefix"}),
  #"Filtered rows" = Table.SelectRows(#"Removed errors", each ([Gender] <> "NA")),
  #"Changed column type" = Table.TransformColumnTypes(#"Filtered rows", {{"AnnualIncome", Currency.Type}}),
  #"Added custom" = Table.AddColumn(#"Changed column type", "Age", each let
Today = Date.From(DateTime.LocalNow()),
BirthDate = Date.From([BirthDate]),
Age = Date.Year(Today) - Date.Year(BirthDate)
in 
Age - (if Date.AddYears(BirthDate, Age) > Today then 1 else 0)),
  #"Added custom 1" = Table.AddColumn(#"Added custom", "Age Group", each if [Age] >= 18 and [Age] < 25 then "18-25"
else if [Age] >= 25 and [Age] < 35 then "25-35"
else if [Age] >= 35 and [Age] < 45 then "35-45"
else if [Age] >= 45 and [Age] < 55 then "45-55"
else if [Age] >= 55 and [Age] < 65 then "55-65"
else if [Age] >= 65 and [Age] < 75 then "65-75"
else if [Age] >= 75 and [Age] < 90 then "75-90"
else if [Age] >= 90 and [Age] < 120 then "90-120"
else null),
  #"Changed column type 1" = Table.TransformColumnTypes(#"Added custom 1", {{"Age Group", type text}})
in
  #"Changed column type 1";
shared customers_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = true, EnableVorder = true, OutputMetadataRefresh = true]),
  Navigation_1 = Pattern{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  Navigation_3 = Navigation_2{[Id = "dbo", ItemKind = "Schema"]}[Data],
  TableNavigation = Navigation_3{[Id = "customers2026", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared DefaultDestination = let
  Source = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = true, EnableVorder = true, OutputMetadataRefresh = true]),
  #"Navigation 1" = Source{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "dbo", ItemKind = "Schema"]}[Data]
in
  #"Navigation 3";
shared returndelta_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = true, EnableVorder = true, OutputMetadataRefresh = true]),
  Navigation_1 = Pattern{[workspaceId = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "c388be50-7662-4217-99c7-ef3401173e52"]}[Data],
  Navigation_3 = Navigation_2{[Id = "dbo", ItemKind = "Schema"]}[Data],
  TableNavigation = Navigation_3{[Id = "returndelta2026", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
