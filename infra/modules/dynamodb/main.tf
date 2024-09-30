resource "aws_dynamodb_table" "digital_assets_table" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "digital_asset_name"  # Updated to match the attribute name

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "digital_asset_name"  # Ensure the attribute matches the range_key
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}