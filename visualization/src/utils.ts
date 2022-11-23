export function map<T, V>(x: T | null, fun: (a: T) => V): V | null {
    return x != null ? fun(x) : null;
}

interface Dict<V> {
    [key: string]: V
}

export function sortDict<V>(dict: Dict<V>, cmp: (a: V, b: V) => number): Dict<V> {
    const items = Object.entries(dict);
    items.sort(([_k1, v1], [_k2, v2]) => cmp(v1, v2))
    return Object.fromEntries(items);
}

export function* enumerate<T>(it: Iterable<T>, start?: number): IterableIterator<[number, T]> {
    let i = start ?? 0;
    for (const el of it) {
        yield [i, el];
        i += 1;
    }
}