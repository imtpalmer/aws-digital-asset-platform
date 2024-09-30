# Outputs
output "dynamodb_table_name" {
  value = aws_dynamodb_table.digital_assets_table.name
}