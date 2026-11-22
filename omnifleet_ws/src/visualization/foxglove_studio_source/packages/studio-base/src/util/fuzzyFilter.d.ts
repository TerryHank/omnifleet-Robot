export default function fuzzyFilter<T>({ options, filter, getText, sort, }: {
    options: T[];
    filter: string | undefined;
    getText: (option: T) => string;
    sort?: boolean;
}): T[];
