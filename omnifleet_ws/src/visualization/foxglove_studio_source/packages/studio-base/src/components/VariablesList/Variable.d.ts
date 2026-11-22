/// <reference types="react" />
import { ListItemButtonProps } from "@mui/material";
export default function Variable(props: {
    name: string;
    selected?: ListItemButtonProps["selected"];
    index: number;
}): JSX.Element;
