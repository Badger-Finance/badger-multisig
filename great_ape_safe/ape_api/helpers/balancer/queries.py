pool_tokens_query = """
        query {
          pools(first: 1000) {
            id
            totalLiquidity
            poolType
            totalWeight
            tokens {
              address
            }
          }
        }
        """
pool_preferential_gauge = """
        query($pool_address: ID!) {
          pool(id: $pool_address) {
            preferentialGauge {
              id
            }
          }
        }
        """
