import torch
import torch.nn as nn
import torch.nn.functional as F

SCALAR_DIM = 19  # castling(4) + ep(8) + side(1) + halfmove(4) + repetition(2)

class ResidualBlock(nn.Module):
    def __init__(self, filters: int):
        super().__init__()
        self.conv1 = nn.Conv2d(filters, filters, kernel_size=3, padding=1, bias=False)
        self.bn1   = nn.BatchNorm2d(filters)
        self.conv2 = nn.Conv2d(filters, filters, kernel_size=3, padding=1, bias=False)
        self.bn2   = nn.BatchNorm2d(filters)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)  # skip connection
        return x

class ChessResNet(nn.Module):
    def __init__(self, num_blocks: int = 8, filters: int = 128):
        super().__init__()

        # Input: [batch, 12, 8, 8], Output: [batch, filters, 8, 8]
        self.input_conv = nn.Sequential(
            nn.Conv2d(12, filters, kernel_size=3, padding=1, bias=False), # torch.Size([128, 12, 3, 3])
            nn.BatchNorm2d(filters), # weights torch.Size([128]), bias torch.Size([128])
            nn.ReLU()
        )

        # Input: [batch, filters, 8, 8], Output: [batch, filters, 8, 8]
        self.tower = nn.Sequential(
            *[ResidualBlock(filters) for _ in range(num_blocks)]
        )

        # Input: [batch, filters, 8, 8], Output: [batch, 32, 8, 8]
        # Basically, compress the feature maps
        self.value_conv = nn.Sequential(
            nn.Conv2d(filters, 32, kernel_size=1, bias=False),  # 1×1 conv to compress
            nn.BatchNorm2d(32),
            nn.ReLU()
        )

        # Input: [batch, 32*8*8 + SCALAR_DIM], Middle: [batch, 256], Output: [batch, 3]
        self.value_fc = nn.Sequential(
            nn.Linear(32 * 8 * 8 + SCALAR_DIM, 256),
            nn.ReLU(),
            nn.Linear(256, 3)  # logits for [loss, draw, win]
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: (batch, 787) float tensor
        Returns:
            logits: (batch, 3) — [loss, draw, win]
        """
        # Split piece planes and scalar features
        planes  = features[:, :768]                  # (batch, 768)
        scalars = features[:, 768:]                  # (batch, 19)

        # Reshape piece planes to (batch, 12, 8, 8)
        x = planes.view(-1, 12, 8, 8)

        # CNN tower
        x = self.input_conv(x)
        x = self.tower(x)

        # Value head
        x = self.value_conv(x)
        x = x.view(x.size(0), -1)                   # flatten → (batch, 32*8*8)
        x = torch.cat([x, scalars], dim=1)           # concat scalars
        logits = self.value_fc(x)

        return logits

    def predict_value(self, features: torch.Tensor) -> torch.Tensor:
        """Returns a scalar in [-1, 1]: p_win - p_loss."""
        logits = self.forward(features)
        probs  = F.softmax(logits, dim=-1)           # (batch, 3)
        return probs[:, 2] - probs[:, 0]             # win - loss