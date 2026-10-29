import { Button, ButtonGroup } from '@mui/material';
import React from 'react';

export interface DoorControlsProps {
  doorName?: string;
  onOpenClick?(event: React.MouseEvent): void;
  onCloseClick?(event: React.MouseEvent): void;
}

export function DoorControls({
  doorName,
  onOpenClick,
  onCloseClick,
}: DoorControlsProps): JSX.Element {
  return (
    <ButtonGroup variant="contained" size="small" sx={{ alignSelf: 'center' }}>
      <Button onClick={onOpenClick} aria-label={`打开-${doorName}`}>
        打开
      </Button>
      <Button onClick={onCloseClick} aria-label={`关闭-${doorName}`}>
        关闭
      </Button>
    </ButtonGroup>
  );
}
