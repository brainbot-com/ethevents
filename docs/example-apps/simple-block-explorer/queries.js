function by_hash(_hash) {
    // query for finding entities (tx, log) by _hash (id or to/from address)
    return {
        query: {bool: {should: [
            {ids: {values: [_hash]}},
            {term: {from: _hash}},
            {term: {to: _hash}},
        ]}},
        sort: {
            timestamp: "desc"
        }
    }
}

function tx_by_blockhash(blockhash) {
    return {
        query: {bool: {filter: { term: {blockHash: blockhash}}}}
    }
}

var latest_block = {
    query: {bool: {filter: {type: {value: "block"}}}},
    sort: {timestamp: "desc"},
    size: 1
}
